#!/usr/bin/env python3
"""Verificar fonte do Kanban sem executar serviços ou consultar a rede."""
from pathlib import Path
import ast
import re
import sys

root = Path(__file__).resolve().parents[1]
manifest = root / "kanban/config.yaml"
server = root / "kanban/server.py"
errors = []
required = [
    manifest, server, root / "kanban/Dockerfile",
    root / "kanban/public/index.html",
    root / "kanban/icon.png", root / "kanban/logo.png",
]
for f in required:
    if not f.is_file() or not f.stat().st_size:
        errors.append("Arquivo obrigatório ausente ou vazio: " + str(f.relative_to(root)))

if manifest.exists() and server.exists():
    y = manifest.read_text(encoding="utf-8")
    py = server.read_text(encoding="utf-8")
    v1 = re.search(r'^version:\s*["\']?([^"\'\s]+)', y, re.M)
    v2 = re.search(r'^VERSION\s*=\s*["\']([^"\']+)', py, re.M)
    if not v1 or not v2 or v1.group(1) != v2.group(1):
        errors.append("Versões incompatíveis entre config.yaml e server.py")
    opts = re.search(r'^options:\s*$([\s\S]*?)^schema:', y, re.M)
    token = re.search(r'^\s+github_token:\s*(.*)$', opts.group(1), re.M) if opts else None
    if not token or token.group(1).strip() not in ('""', "''", ''):
        errors.append("Valor padrão github_token deve estar vazio no manifesto público")
    owner_kind = re.search(r'^\s+github_owner_type:\s*["\']?([^"\'\s]+)', opts.group(1), re.M) if opts else None
    schema = y.split("\nschema:", 1)[1] if "\nschema:" in y else ""
    if not owner_kind or owner_kind.group(1) != "user":
        errors.append("github_owner_type deve ter padrao user")
    if not re.search(r'^\s+github_owner_type:\s*["\']list\(user\|organization\)["\']\s*
        errors.append("Slug alterado; conferir compatibilidade antes da publicação")
    try:
        ast.parse(py, filename="server.py")
    except SyntaxError:
        errors.append("Sintaxe de server.py inválida")

if errors:
    for e in errors:
        print("ERRO:", e)
    sys.exit(1)
print("OK: arquivos essenciais, versão coerente, manifesto sem token e sintaxe Python")
, schema, re.M):
        errors.append("Esquema github_owner_type deve permitir user e organization")
    if not re.search(r'^\s*slug:\s*kanban\s*
        errors.append("Slug alterado; conferir compatibilidade antes da publicação")
    try:
        ast.parse(py, filename="server.py")
    except SyntaxError:
        errors.append("Sintaxe de server.py inválida")

if errors:
    for e in errors:
        print("ERRO:", e)
    sys.exit(1)
print("OK: arquivos essenciais, versão coerente, manifesto sem token e sintaxe Python")
, y, re.M):
        errors.append("Slug alterado; conferir compatibilidade antes da publicação")
    try:
        ast.parse(py, filename="server.py")
    except SyntaxError:
        errors.append("Sintaxe de server.py inválida")

if errors:
    for e in errors:
        print("ERRO:", e)
    sys.exit(1)
print("OK: arquivos essenciais, versão coerente, manifesto sem token e sintaxe Python")
