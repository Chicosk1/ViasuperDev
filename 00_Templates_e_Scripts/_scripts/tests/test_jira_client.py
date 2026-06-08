"""
test_jira_client.py — Testes unitários para jira_client.py.
"""

from __future__ import annotations

import pytest

from viasuperdev.jira_client import JiraClient, JiraIssue


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_raw_issue(**overrides) -> dict:
    """Simula o JSON bruto retornado pela API do Jira."""
    fields = {
        "summary":    "Ticket de teste",
        "description": {},
        "status":     {"name": "Backlog"},
        "issuetype":  {"name": "Melhoria"},
        "priority":   {"name": "Medium"},
        "assignee":   {"displayName": "Dev Teste"},
        "reporter":   {"displayName": "PO Teste"},
        "created":    "2026-01-15T10:30:00.000-0300",
        "updated":    "2026-05-20T08:00:00.000-0300",
        "components": [],
        "labels":     [],
        "customfield_10150": None,
        "fixVersions": [],
    }
    fields.update(overrides)
    return {"key": "AG-99999", "fields": fields}


# ── Testes: _parse_date ───────────────────────────────────────────────────────

class TestParseDate:
    def test_extrai_data_de_timestamp_jira(self):
        result = JiraClient._parse_date("2026-03-09T15:10:15.341-0300")
        assert result == "2026-03-09"

    def test_data_vazia_retorna_hoje(self):
        from datetime import date
        result = JiraClient._parse_date("")
        assert result == date.today().isoformat()

    def test_data_curta_sem_timestamp(self):
        result = JiraClient._parse_date("2026-01-01")
        assert result == "2026-01-01"


# ── Testes: _extract_versao ───────────────────────────────────────────────────

class TestExtractVersao:
    def test_extrai_de_customfield_10150(self):
        fields = {
            "customfield_10150": [
                {"name": "5.0.2604.xxxx - Lote 734 - Viasuper"}
            ],
            "fixVersions": [],
        }
        assert JiraClient._extract_versao(fields) == "5.0.2604.xxxx"

    def test_extrai_de_fixVersions_como_fallback(self):
        fields = {
            "customfield_10150": None,
            "fixVersions": [
                {"name": "2026.1 - Lote 700 - Viasuper"}
            ],
        }
        assert JiraClient._extract_versao(fields) == "2026.1"

    def test_retorna_vazio_quando_sem_versao(self):
        fields = {"customfield_10150": None, "fixVersions": []}
        assert JiraClient._extract_versao(fields) == ""

    def test_prioriza_customfield_sobre_fixVersions(self):
        fields = {
            "customfield_10150": [{"name": "5.0.2604.xxxx - Lote 734"}],
            "fixVersions":       [{"name": "5.0.2500.xxxx - Lote 700"}],
        }
        assert JiraClient._extract_versao(fields) == "5.0.2604.xxxx"

    def test_nome_sem_separador_retorna_nome_completo(self):
        fields = {
            "customfield_10150": [{"name": "2026.1"}],
            "fixVersions": [],
        }
        assert JiraClient._extract_versao(fields) == "2026.1"


# ── Testes: _parse_issue ──────────────────────────────────────────────────────

class TestParseIssue:
    def _client(self) -> JiraClient:
        return JiraClient("https://example.atlassian.net", "u@e.com", "token")

    def test_mapeia_campos_basicos(self):
        raw    = make_raw_issue()
        client = self._client()
        issue  = client._parse_issue(raw)

        assert issue.key     == "AG-99999"
        assert issue.summary == "Ticket de teste"
        assert issue.status  == "Backlog"
        assert issue.priority == "Medium"
        assert issue.assignee == "Dev Teste"
        assert issue.reporter == "PO Teste"

    def test_url_construida_corretamente(self):
        raw    = make_raw_issue()
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.url == "https://example.atlassian.net/browse/AG-99999"

    def test_data_criacao_formatada(self):
        raw    = make_raw_issue()
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.created == "2026-01-15"

    def test_versao_sistema_extraida(self):
        raw = make_raw_issue(**{
            "customfield_10150": [{"name": "5.0.2604.xxxx - Lote 734 - Viasuper"}]
        })
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.versao_sistema == "5.0.2604.xxxx"

    def test_assignee_none_vira_string_vazia(self):
        raw = make_raw_issue(**{"assignee": None})
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.assignee == ""

    def test_priority_none_usa_fallback_medium(self):
        # _parse_issue usa safe() com default="Medium" para priority
        raw = make_raw_issue(**{"priority": None})
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.priority == "Medium"

    def test_components_extraidos_como_lista(self):
        raw = make_raw_issue(**{
            "components": [{"name": "Nota Fiscal"}, {"name": "Financeiro"}]
        })
        client = self._client()
        issue  = client._parse_issue(raw)
        assert issue.components == ["Nota Fiscal", "Financeiro"]