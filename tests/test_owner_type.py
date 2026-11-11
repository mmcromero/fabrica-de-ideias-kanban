"""Testes offline da escolha de proprietário no GitHub Projects V2."""
import unittest
from unittest.mock import patch

from kanban import server as app


class OwnerConfigTests(unittest.TestCase):
    def test_legacy_options_use_personal_account(self):
        legacy = {
            "github_owner": "conta-exemplo",
            "github_token": "token-de-teste",
            "github_project_number": 4,
            "github_status_field": "Status",
            "github_hidden_projects": "2, 7",
        }
        with patch.object(app, "load_options", return_value=legacy):
            config = app.cfg()
        self.assertEqual(config["owner_type"], "user")
        self.assertEqual(config["owner"], "conta-exemplo")
        self.assertEqual(config["number"], 4)
        self.assertEqual(config["hidden"], {2, 7})
        self.assertEqual(config["field"], "Status")

    def test_explicit_organization(self):
        with patch.object(app, "load_options", return_value={
            "github_owner": "organizacao-exemplo",
            "github_token": "token-de-teste",
            "github_owner_type": "organization",
        }):
            config = app.cfg()
        self.assertEqual(config["owner_type"], "organization")
        self.assertEqual(config["owner"], "organizacao-exemplo")

    def test_invalid_owner_type_is_rejected(self):
        with patch.object(app, "load_options", return_value={
            "github_owner": "conta-exemplo",
            "github_token": "token-de-teste",
            "github_owner_type": "project",
        }):
            with self.assertRaises(app.ConfigError):
                app.cfg()

    def test_missing_owner_and_token_still_rejected(self):
        for options in (
            {"github_token": "token-de-teste"},
            {"github_owner": "conta-exemplo"},
        ):
            with self.subTest(options=list(options)):
                with patch.object(app, "load_options", return_value=options):
                    with self.assertRaises(app.ConfigError):
                        app.cfg()


class OwnerQueryTests(unittest.TestCase):
    def test_owner_lookup_uses_selected_type(self):
        for kind in ("user", "organization"):
            with self.subTest(kind=kind):
                with patch.object(app, "gql", return_value={"owner": {"id": "OWNER_ID"}}) as gql:
                    result = app.owner_data({"owner": "conta-exemplo", "owner_type": kind})
                self.assertEqual(result["id"], "OWNER_ID")
                self.assertIn(f"owner: {kind}(login: $login)", gql.call_args.args[0])
                self.assertEqual(gql.call_args.args[1], {"login": "conta-exemplo"})

    def test_legacy_owner_lookup_defaults_to_user(self):
        with patch.object(app, "gql", return_value={"owner": {"id": "PERSONAL_ID"}}) as gql:
            result = app.owner_data({"owner": "conta-exemplo"})
        self.assertEqual(result["id"], "PERSONAL_ID")
        self.assertIn("owner: user(login: $login)", gql.call_args.args[0])

    def test_projects_are_paginated_for_both_types(self):
        for kind in ("user", "organization"):
            with self.subTest(kind=kind):
                config = {"owner": "conta-exemplo", "owner_type": kind}
                pages = [
                    {"owner": {"projectsV2": {
                        "nodes": [
                            {"id": "P1", "number": 1, "title": "Primeiro", "closed": False},
                            {"id": "P2", "number": 2, "title": "Fechado", "closed": True},
                        ],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-2"},
                    }}},
                    {"owner": {"projectsV2": {
                        "nodes": [{"id": "P3", "number": 3, "title": "Segundo", "closed": False}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }}},
                ]
                with patch.object(app, "gql", side_effect=pages) as gql:
                    projects = app.all_projects(config)
                self.assertEqual([p["number"] for p in projects], [1, 3])
                self.assertEqual(gql.call_count, 2)
                self.assertIn(f"owner: {kind}(login: $login)", gql.call_args_list[0].args[0])
                self.assertEqual(gql.call_args_list[0].args[1]["after"], None)
                self.assertEqual(gql.call_args_list[1].args[1]["after"], "cursor-2")

    def test_permission_error_is_not_swallowed(self):
        with patch.object(app, "gql", side_effect=app.ApiError("Sem permissao")):
            with self.assertRaises(app.ApiError):
                app.all_projects({"owner": "org-exemplo", "owner_type": "organization"})

    def test_unrecognized_kind_does_not_enter_graphql(self):
        with patch.object(app, "gql") as gql:
            with self.assertRaises(app.ConfigError):
                app.owner_data({"owner": "conta-exemplo", "owner_type": "other"})
            gql.assert_not_called()

    def test_project_creation_uses_correct_owner_id(self):
        for kind in ("user", "organization"):
            with self.subTest(kind=kind):
                config = {"owner": "conta-exemplo", "owner_type": kind, "field": "Status"}
                queries = []

                def fake_gql(query, variables):
                    queries.append((query, variables))
                    if "owner: " in query:
                        return {"owner": {"id": f"{kind}-id"}}
                    if "createProjectV2" in query:
                        self.assertEqual(variables["owner"], f"{kind}-id")
                        return {"createProjectV2": {
                            "projectV2": {"id": "NEW_ID", "number": 12, "title": "Novo quadro"}
                        }}
                    if "updateProjectV2Field" in query:
                        return {"updateProjectV2Field": {
                            "projectV2Field": {"options": [
                                {"id": "STATUS_1", "name": "A fazer", "color": "BLUE"},
                            ]}
                        }}
                    raise AssertionError("Consulta inesperada")

                field = {"id": "FIELD_ID", "options": [
                    {"id": "STATUS_1", "name": "Status", "color": "BLUE"},
                ]}
                with patch.object(app, "cfg", return_value=config), \
                     patch.object(app, "all_projects", return_value=[]), \
                     patch.object(app, "field_for", return_value=field), \
                     patch.object(app, "audit"), \
                     patch.object(app, "gql", side_effect=fake_gql):
                    response = app.create_project({"title": "Novo quadro"}, "usuario-ha")
                self.assertEqual(response["project"]["id"], "NEW_ID")
                self.assertEqual(response["aviso"], "")
                self.assertIn(f"owner: {kind}(login: $login)", queries[0][0])


if __name__ == "__main__":
    unittest.main()
