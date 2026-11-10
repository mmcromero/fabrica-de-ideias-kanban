#!/usr/bin/env python3
"""Fábrica de Ideias Kanban (GitHub Projects V2).

Acesso somente pelo Ingress do Home Assistant. Token e dono vêm das opções do
add-on. Cada Project do dono vira um quadro, exceto os ocultados nas opções.
A ordem das abas fica em /data/board_order.json. Usa só a biblioteca padrão.
"""
from __future__ import annotations

import ipaddress
import json
import logging
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, quote, urlsplit

VERSION = '0.0.25'
STATIC_DIR = '/app/public'
OPTIONS_FILE = Path('/data/options.json')
AUDIT_FILE = Path('/data/audit.jsonl')
ORDER_FILE = Path('/data/board_order.json')
GRAPHQL_URL = 'https://api.github.com/graphql'
REST_URL = 'https://api.github.com'
SUPERVISOR_ADDRESS = ipaddress.ip_address('172.30.32.2')
MAX_BODY = 32768
MAX_COLUMNS = 20
MAX_BOARDS = 200
NEW_BOARD_COLUMNS = ['A fazer', 'Em execução', 'Concluído']
COLOR_CYCLE = ['BLUE', 'YELLOW', 'GREEN', 'PURPLE', 'ORANGE', 'RED', 'PINK', 'GRAY']
BODY_LIMIT = 20000
LOG = logging.getLogger('kanban')
WRITE_LOCK = Lock()


class ConfigError(Exception):
    pass


class ApiError(Exception):
    pass


class Conflict(Exception):
    pass


# ---------- GraphQL ----------
# Só as de leitura, movimentação, ordem e colunas foram testadas.
# OWNER_QUERY, PROJECTS_QUERY, CREATE_MUTATION e o campo body em ITEMS_QUERY são novos.

OWNER_QUERY = """
query($login: String!) { user(login: $login) { id } }
"""

PROJECTS_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    projectsV2(first: 50, after: $after) {
      pageInfo { hasNextPage endCursor }
      nodes { id number title closed }
    }
  }
}
"""

FIELDS_QUERY = """
query($id: ID!) {
  node(id: $id) {
    ... on ProjectV2 {
      id
      fields(first: 50) {
        nodes { ... on ProjectV2SingleSelectField { id name options { id name color } } }
      }
    }
  }
}
"""

ITEMS_QUERY = """
query($id: ID!, $after: String, $field: String!) {
  node(id: $id) {
    ... on ProjectV2 {
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          updatedAt
          content {
            __typename
            ... on Issue { number title url state }
            ... on DraftIssue { title body }
          }
          fieldValueByName(name: $field) {
            ... on ProjectV2ItemFieldSingleSelectValue { optionId name }
          }
        }
      }
    }
  }
}
"""

CREATE_MUTATION = """
mutation($owner: ID!, $title: String!) {
  createProjectV2(input: {ownerId: $owner, title: $title}) {
    projectV2 { id number title }
  }
}
"""

CREATE_DRAFT_MUTATION = """
mutation($project: ID!, $title: String!, $body: String) {
  addProjectV2DraftIssue(input: {projectId: $project, title: $title, body: $body}) {
    projectItem { id }
  }
}
"""

MOVE_MUTATION = """
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field,
    value: { singleSelectOptionId: $option }
  }) { projectV2Item { id } }
}
"""

REORDER_MUTATION = """
mutation($project: ID!, $item: ID!, $after: ID) {
  updateProjectV2ItemPosition(input: {projectId: $project, itemId: $item, afterId: $after}) {
    items(first: 1) { totalCount }
  }
}
"""

FIELD_MUTATION = """
mutation($field: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
  updateProjectV2Field(input: {fieldId: $field, singleSelectOptions: $options}) {
    projectV2Field { ... on ProjectV2SingleSelectField { id options { id name color } } }
  }
}
"""


# ---------- Configuração, ordem e auditoria ----------

def load_options() -> dict:
    try:
        obj = json.loads(OPTIONS_FILE.read_text(encoding='utf-8'))
        return obj if isinstance(obj, dict) else {}
    except FileNotFoundError:
        return {}


def cfg() -> dict:
    o = load_options()
    owner = str(o.get('github_owner') or '').strip()
    token = str(o.get('github_token') or '').strip()
    field = str(o.get('github_status_field') or 'Status').strip() or 'Status'
    try:
        number = int(o.get('github_project_number') or 0)
    except (TypeError, ValueError):
        number = 0
    hidden = {int(n) for n in re.findall(r'\d+', str(o.get('github_hidden_projects') or ''))}
    if not owner:
        raise ConfigError('Configure github_owner nas opções do add-on')
    if not token:
        raise ConfigError('Configure github_token nas opções do add-on')
    return {'owner': owner, 'token': token, 'field': field, 'number': number, 'hidden': hidden}


def load_order() -> list:
    try:
        obj = json.loads(ORDER_FILE.read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        return []
    if not isinstance(obj, list):
        return []
    return [int(n) for n in obj if isinstance(n, int) and not isinstance(n, bool) and n > 0]


def save_order(numbers: list) -> None:
    ORDER_FILE.write_text(json.dumps(numbers, ensure_ascii=False), encoding='utf-8')


def audit(entry: dict) -> None:
    """Rastreabilidade local. O histórico do método antigo (comentário na Issue) fica na documentação."""
    line = {'ts': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'versao': VERSION, **entry}
    with AUDIT_FILE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(line, ensure_ascii=False) + '\n')


def gql(query: str, variables: dict) -> dict:
    token = cfg()['token']
    body = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
    req = urllib.request.Request(GRAPHQL_URL, data=body, headers={
        'Authorization': 'bearer ' + token,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'AD-Kanban/' + VERSION,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as exc:
        raise ApiError(f'GitHub respondeu HTTP {exc.code}') from None
    except (urllib.error.URLError, TimeoutError):
        raise ApiError('Falha de rede ao falar com o GitHub') from None
    if data.get('errors'):
        raise ApiError(str(data['errors'][0].get('message', 'erro GraphQL'))[:300])
    return data.get('data') or {}


def rest_get(path: str) -> dict:
    token = cfg()['token']
    req = urllib.request.Request(REST_URL + path, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'AD-Kanban/' + VERSION,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as exc:
        raise ApiError(f'GitHub respondeu HTTP {exc.code} ao ler a Issue') from None
    except (urllib.error.URLError, TimeoutError):
        raise ApiError('Falha de rede ao falar com o GitHub') from None


# ---------- Quadros (Projects) ----------

def all_projects(c: dict) -> list:
    out, after = [], None
    while True:
        conn = (((gql(PROJECTS_QUERY, {'login': c['owner'], 'after': after}).get('user') or {})
                 .get('projectsV2')) or {})
        for p in conn.get('nodes', []):
            if p and not p.get('closed'):
                out.append({'id': p['id'], 'number': p['number'], 'title': p['title']})
        info = conn.get('pageInfo') or {}
        if not info.get('hasNextPage'):
            break
        after = info.get('endCursor')
    return out


def visible_projects(c: dict) -> list:
    visible = [p for p in all_projects(c) if p['number'] not in c['hidden']]
    rank = {n: i for i, n in enumerate(load_order())}
    return sorted(visible, key=lambda p: (rank.get(p['number'], len(rank) + 1),
                                          p['title'].casefold(), p['number']))


def default_project_id(c: dict, visible: list):
    if c['number']:
        match = next((p for p in visible if p['number'] == c['number']), None)
        if match:
            return match['id']
    return visible[0]['id'] if visible else None


def project_id_from(c: dict, raw: str) -> str:
    pid = str(raw or '').strip()
    if not pid:
        raise ValueError('Quadro não informado')
    if pid not in {p['id'] for p in visible_projects(c)}:
        raise ValueError('Quadro não encontrado ou oculto nas opções do add-on')
    return pid


def field_for(pid: str, field_name: str) -> dict:
    data = gql(FIELDS_QUERY, {'id': pid})
    node = data.get('node') or {}
    fields = ((node.get('fields') or {}).get('nodes')) or []
    f = next((x for x in fields if x and x.get('name') == field_name), None)
    if not f:
        raise ApiError(f'Campo "{field_name}" (single select) não existe neste quadro')
    return f


def board_data(c: dict, pid: str) -> dict:
    fld = field_for(pid, c['field'])
    columns = [{'id': o['id'], 'name': o['name'], 'color': o['color']} for o in (fld.get('options') or [])]
    items, after = [], None
    while True:
        conn = (((gql(ITEMS_QUERY, {'id': pid, 'after': after, 'field': c['field']}).get('node') or {})
                 .get('items')) or {})
        for n in conn.get('nodes', []):
            content = n.get('content') or {}
            fv = n.get('fieldValueByName') or {}
            is_issue = content.get('__typename') == 'Issue'
            items.append({
                'id': n['id'],
                'kind': 'issue' if is_issue else 'draft',
                'number': content.get('number') if is_issue else None,
                'title': content.get('title') or '(sem título)',
                'url': content.get('url') if is_issue else None,
                'state': content.get('state'),
                'column_id': fv.get('optionId'),
                'updated_at': n.get('updatedAt'),
                'body': content.get('body') if not is_issue else None,
            })
        info = conn.get('pageInfo') or {}
        if not info.get('hasNextPage'):
            break
        after = info.get('endCursor')
    return {'columns': columns, 'items': items, 'field_id': fld['id']}


def find(items: list, item_id: str):
    return next((i for i in items if i['id'] == item_id), None)


def strip_items_body(items: list) -> list:
    """O corpo de rascunhos não vai para o quadro; só para a janela do card."""
    return [{k: v for k, v in i.items() if k != 'body'} for i in items]


# ---------- Leitura ----------

def list_projects_response() -> dict:
    c = cfg()
    visible = visible_projects(c)
    return {
        'projects': [{'id': p['id'], 'number': p['number'], 'title': p['title']} for p in visible],
        'default': default_project_id(c, visible),
        'version': VERSION,
    }


def board_response(raw_pid: str) -> dict:
    c = cfg()
    pid = project_id_from(c, raw_pid) if raw_pid else default_project_id(c, visible_projects(c))
    if not pid:
        raise ValueError('Nenhum quadro visível. Crie um pelo botão + Novo quadro.')
    data = board_data(c, pid)
    return {'project': pid, 'columns': data['columns'], 'items': strip_items_body(data['items']),
            'rules': {}, 'version': VERSION}


def card_response(raw_pid: str, item_id: str) -> dict:
    """Somente leitura. Rascunho: corpo vem do quadro. Issue: corpo vem da API de Issues."""
    c = cfg()
    pid = project_id_from(c, raw_pid)
    if not item_id:
        raise ValueError('Card não informado')
    b = board_data(c, pid)
    item = find(b['items'], item_id)
    if not item:
        raise ValueError('Card não encontrado no quadro')
    col = next((x for x in b['columns'] if x['id'] == item['column_id']), None)
    out = {
        'id': item['id'],
        'kind': item['kind'],
        'number': item['number'],
        'title': item['title'],
        'url': item['url'],
        'state': item['state'],
        'column': col['name'] if col else 'Sem status',
        'labels': [],
        'assignees': [],
        'body': '',
        'body_error': '',
    }
    if item['kind'] == 'draft':
        out['body'] = (item.get('body') or '')[:BODY_LIMIT]
        return out
    # Issue: lê título, corpo, labels e responsáveis pela API REST de Issues.
    repo_url = item['url'] or ''
    parts = repo_url.split('/')
    if len(parts) < 7:
        out['body_error'] = 'Não foi possível identificar o repositório da Issue'
        return out
    owner, repo = parts[3], parts[4]
    try:
        data = rest_get(f'/repos/{quote(owner)}/{quote(repo)}/issues/{int(item["number"])}')
    except ApiError as exc:
        out['body_error'] = str(exc)
        return out
    out['title'] = data.get('title') or out['title']
    out['state'] = data.get('state') or out['state']
    out['labels'] = [x.get('name') for x in data.get('labels') or [] if isinstance(x, dict) and x.get('name')]
    out['assignees'] = [x.get('login') for x in data.get('assignees') or [] if isinstance(x, dict) and x.get('login')]
    out['body'] = (data.get('body') or '')[:BODY_LIMIT]
    return out


# ---------- Escritas ----------

def move_card(p: dict, actor: str) -> dict:
    c = cfg()
    pid = project_id_from(c, p.get('project'))
    item_id = str(p.get('item_id') or '')
    to = str(p.get('to_column_id') or '')
    expected = p.get('expected_column_id') or None
    if not item_id or not to:
        raise ValueError('item_id e to_column_id são obrigatórios')
    with WRITE_LOCK:
        b = board_data(c, pid)
        item = find(b['items'], item_id)
        if not item:
            raise ValueError('Card não encontrado no quadro')
        if item['column_id'] != expected:
            raise Conflict('O card mudou no GitHub. Atualize o quadro antes de mover.')
        if item['column_id'] == to:
            raise ValueError('O card já está nessa coluna')
        if to not in {col['id'] for col in b['columns']}:
            raise ValueError('Coluna de destino inexistente')
        gql(MOVE_MUTATION, {'project': pid, 'item': item_id, 'field': b['field_id'], 'option': to})
        after = find(board_data(c, pid)['items'], item_id)
        verified = bool(after and after['column_id'] == to)
        audit({'acao': 'mover', 'actor': actor, 'projeto': pid, 'item': item_id,
               'numero': item.get('number'), 'de': item['column_id'], 'para': to, 'verificado': verified})
        return {'verified': verified}


def reorder_card(p: dict, actor: str) -> dict:
    c = cfg()
    pid = project_id_from(c, p.get('project'))
    item_id = str(p.get('item_id') or '')
    after_id = str(p.get('after_item_id') or '') or None
    if not item_id:
        raise ValueError('item_id é obrigatório')
    with WRITE_LOCK:
        b = board_data(c, pid)
        item = find(b['items'], item_id)
        if not item:
            raise ValueError('Card não encontrado no quadro')
        if after_id:
            anchor = find(b['items'], after_id)
            if not anchor or anchor['column_id'] != item['column_id']:
                raise ValueError('O card de referência precisa estar na mesma coluna')
        gql(REORDER_MUTATION, {'project': pid, 'item': item_id, 'after': after_id})
        ordered = [i['id'] for i in board_data(c, pid)['items'] if i['column_id'] == item['column_id']]
        verified = (ordered.index(item_id) == ordered.index(after_id) + 1) if after_id else ordered[:1] == [item_id]
        audit({'acao': 'ordenar', 'actor': actor, 'projeto': pid, 'item': item_id,
               'depois_de': after_id, 'coluna': item['column_id'], 'verificado': verified})
        return {'verified': verified}


def update_columns(p: dict, actor: str) -> dict:
    c = cfg()
    pid = project_id_from(c, p.get('project'))
    incoming = p.get('columns')
    if not isinstance(incoming, list) or not (1 <= len(incoming) <= MAX_COLUMNS):
        raise ValueError(f'Envie de 1 a {MAX_COLUMNS} colunas')
    names_seen = set()
    for idx, col in enumerate(incoming):
        if not isinstance(col, dict):
            raise ValueError('Coluna inválida')
        name = str(col.get('name') or '').strip()
        if not (1 <= len(name) <= 40):
            raise ValueError('Cada coluna precisa de nome com até 40 caracteres')
        if name.casefold() in names_seen:
            raise ValueError(f'Nome repetido: "{name}"')
        names_seen.add(name.casefold())
        col['name'] = name
        color = str(col.get('color') or COLOR_CYCLE[idx % len(COLOR_CYCLE)]).upper()
        if color not in COLOR_CYCLE:
            raise ValueError(f'Cor inválida para "{name}". Use uma das 8 cores do GitHub.')
        col['color'] = color
    with WRITE_LOCK:
        b = board_data(c, pid)
        current = {col['id']: col for col in b['columns']}
        keep = set()
        for col in incoming:
            cid = col.get('id')
            if cid:
                if cid not in current:
                    raise ValueError('Coluna desconhecida enviada para edição')
                keep.add(cid)
        for cid, col in current.items():
            if cid in keep:
                continue
            n = sum(1 for i in b['items'] if i['column_id'] == cid)
            if n:
                raise ValueError(f'A coluna "{col["name"]}" tem {n} card(s). Mova-os antes de apagar.')
        options = []
        for col in incoming:
            opt = {'name': col['name'], 'description': '', 'color': col['color']}
            if col.get('id'):
                opt['id'] = col['id']
            options.append(opt)
        result = gql(FIELD_MUTATION, {'field': b['field_id'], 'options': options})
        new_opts = (((result.get('updateProjectV2Field') or {}).get('projectV2Field') or {})
                    .get('options'))
        if not isinstance(new_opts, list) or len(new_opts) != len(incoming):
            raise ApiError('GitHub não confirmou a nova lista de colunas')
        cor_confirmada = all(new_opts[i].get('color') == incoming[i]['color'] for i in range(len(incoming)))
        audit({'acao': 'colunas', 'actor': actor, 'projeto': pid,
               'antes': [x['name'] for x in b['columns']],
               'depois': [o['name'] for o in new_opts],
               'cores_depois': [o.get('color') for o in new_opts],
               'cor_confirmada': cor_confirmada})
        return {'columns': [{'id': o['id'], 'name': o['name'], 'color': o['color']} for o in new_opts]}


def create_project(p: dict, actor: str) -> dict:
    title = str(p.get('title') or '').strip()
    if not (1 <= len(title) <= 100):
        raise ValueError('O nome do quadro precisa ter de 1 a 100 caracteres')
    c = cfg()
    with WRITE_LOCK:
        existing = all_projects(c)
        if any(x['title'].casefold() == title.casefold() for x in existing):
            raise ValueError('Já existe um quadro com este nome no GitHub')
        owner_id = (gql(OWNER_QUERY, {'login': c['owner']}).get('user') or {}).get('id')
        if not owner_id:
            raise ApiError('Não foi possível localizar o dono configurado')
        created = (gql(CREATE_MUTATION, {'owner': owner_id, 'title': title})
                   .get('createProjectV2') or {}).get('projectV2')
        if not created:
            raise ApiError('GitHub não confirmou a criação do quadro')
        pid = created['id']
        aviso = ''
        try:
            fld = field_for(pid, c['field'])
            options = []
            for i, o in enumerate(fld.get('options') or []):
                name = NEW_BOARD_COLUMNS[i] if i < len(NEW_BOARD_COLUMNS) else o['name']
                options.append({'id': o['id'], 'name': name, 'description': '', 'color': o['color']})
            gql(FIELD_MUTATION, {'field': fld['id'], 'options': options})
        except ApiError as exc:
            aviso = f'Colunas não renomeadas ({exc}). Renomeie pela janela de colunas.'
            LOG.warning('Criação de quadro: %s', exc)
        audit({'acao': 'criar_quadro', 'actor': actor, 'projeto': pid,
               'numero': created.get('number'), 'titulo': title, 'aviso': aviso})
        return {'project': {'id': pid, 'number': created.get('number'), 'title': title},
                'aviso': aviso}

def create_card(p: dict, actor: str) -> dict:
    """Cria um rascunho no quadro e o coloca na coluna escolhida (dois passos, como nos testes)."""
    c = cfg()
    pid = project_id_from(c, p.get('project'))
    title = str(p.get('title') or '').strip()
    body = str(p.get('body') or '').strip()[:BODY_LIMIT]
    to = str(p.get('to_column_id') or '')
    if not (1 <= len(title) <= 200):
        raise ValueError('O título do card precisa ter de 1 a 200 caracteres')
    if not to:
        raise ValueError('Escolha a coluna do card')
    with WRITE_LOCK:
        b = board_data(c, pid)
        if to not in {col['id'] for col in b['columns']}:
            raise ValueError('Coluna de destino inexistente')
        created = ((gql(CREATE_DRAFT_MUTATION, {'project': pid, 'title': title, 'body': body or None})
                    .get('addProjectV2DraftIssue') or {}).get('projectItem') or {})
        item_id = created.get('id')
        if not item_id:
            raise ApiError('GitHub não confirmou a criação do card')
        aviso = ''
        verified = False
        try:
            gql(MOVE_MUTATION, {'project': pid, 'item': item_id, 'field': b['field_id'], 'option': to})
            after = find(board_data(c, pid)['items'], item_id)
            verified = bool(after and after['column_id'] == to)
        except ApiError as exc:
            aviso = f'Card criado, mas não foi possível colocá-lo na coluna ({exc}). Ele está em "Sem status".'
        audit({'acao': 'criar_card', 'actor': actor, 'projeto': pid, 'item': item_id,
               'para': to, 'titulo': title, 'verificado': verified, 'aviso': aviso})
        return {'verified': verified, 'item_id': item_id, 'aviso': aviso}

def save_board_order(p: dict, actor: str) -> dict:
    c = cfg()
    ids = p.get('projects')
    if not isinstance(ids, list) or len(ids) > MAX_BOARDS:
        raise ValueError('Envie a lista de quadros em ordem')
    visible = {p_['id']: p_['number'] for p_ in visible_projects(c)}
    numbers = []
    for raw in ids:
        pid = str(raw or '')
        if pid not in visible:
            raise ValueError('Quadro não encontrado ou oculto nas opções do add-on')
        numbers.append(visible[pid])
    if len(set(numbers)) != len(numbers):
        raise ValueError('Lista de quadros com repetição')
    with WRITE_LOCK:
        previous = [n for n in load_order() if n not in set(numbers)]
        save_order(numbers + previous)
    audit({'acao': 'ordenar_quadros', 'actor': actor, 'ordem': numbers})
    return {'order': numbers}


# ---------- HTTP ----------

class Handler(SimpleHTTPRequestHandler):
    server_version = 'AD-Kanban/' + VERSION
    sys_version = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, fmt, *args):
        LOG.info('%s %s', self.client_address[0], fmt % args)

    def _ingress(self) -> bool:
        try:
            return ipaddress.ip_address(self.client_address[0]) == SUPERVISOR_ADDRESS
        except ValueError:
            return False

    def _json(self, status_code: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _call(self, fn):
        try:
            result = fn()
            self._json(200, {'success': True, **(result if isinstance(result, dict) else {})})
        except Conflict as exc:
            self._json(409, {'success': False, 'error': str(exc)})
        except ConfigError as exc:
            self._json(503, {'success': False, 'error': str(exc)})
        except ApiError as exc:
            LOG.warning('GitHub: %s', exc)
            self._json(502, {'success': False, 'error': str(exc)})
        except ValueError as exc:
            self._json(400, {'success': False, 'error': str(exc)})

    def do_GET(self):
        if not self._ingress():
            self._json(403, {'success': False, 'error': 'Acesso permitido somente via Ingress'})
            return
        parsed = urlsplit(self.path)
        path = parsed.path
        q = parse_qs(parsed.query)
        if path == '/api/projects':
            return self._call(list_projects_response)
        if path == '/api/board':
            raw = (q.get('project') or [''])[0]
            return self._call(lambda: board_response(raw))
        if path == '/api/card':
            raw = (q.get('project') or [''])[0]
            item = (q.get('item') or [''])[0]
            return self._call(lambda: card_response(raw, item))
        if path.startswith('/api/'):
            self._json(404, {'success': False, 'error': 'API desconhecida'})
            return
        return super().do_GET()

    def do_POST(self):
        if not self._ingress():
            self._json(403, {'success': False, 'error': 'Acesso permitido somente via Ingress'})
            return
        routes = {
            '/api/move': move_card,
            '/api/reorder': reorder_card,
            '/api/columns': update_columns,
            '/api/projects/create': create_project,
            '/api/projects/order': save_board_order,
            '/api/cards/create': create_card,
        }
        path = urlsplit(self.path).path
        if path not in routes:
            self._json(404, {'success': False, 'error': 'API desconhecida'})
            return
        actor = self.headers.get('X-Remote-User-Id', '').strip()
        if not actor or len(actor) > 128:
            self._json(403, {'success': False, 'error': 'Usuário do Ingress não identificado. Escrita bloqueada.'})
            return
        if self.headers.get('X-Requested-With') != 'XMLHttpRequest':
            self._json(403, {'success': False, 'error': 'Cabeçalho de solicitação ausente'})
            return
        if self.headers.get('Content-Type', '').split(';', 1)[0].strip().lower() != 'application/json':
            self._json(415, {'success': False, 'error': 'Content-Type deve ser application/json'})
            return
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if not (0 < n <= MAX_BODY):
                raise ValueError('Tamanho inválido')
            payload = json.loads(self.rfile.read(n))
            if not isinstance(payload, dict):
                raise ValueError('Corpo deve ser um objeto JSON')
        except (ValueError, TypeError):
            self._json(400, {'success': False, 'error': 'Corpo da requisição inválido'})
            return
        fn = routes[path]
        self._call(lambda: fn(payload, actor))

    def do_OPTIONS(self):
        self._json(405, {'success': False, 'error': 'Método não autorizado'})


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    LOG.info('Iniciando Fábrica de Ideias Kanban %s na porta 8099 (GitHub Projects V2)', VERSION)
    ThreadingHTTPServer(('0.0.0.0', 8099), Handler).serve_forever()