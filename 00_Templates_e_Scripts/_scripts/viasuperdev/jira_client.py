"""
jira_client.py — Cliente HTTP para a API do Jira.

Responsabilidade única: comunicação com o Jira.
Nenhuma lógica de negócio ou escrita de arquivos aqui.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from viasuperdev import config

log = logging.getLogger(__name__)


# ── Modelos de dados ──────────────────────────────────────────────────────────

@dataclass
class JiraIssue:
    """Representação limpa de um ticket Jira — sem dependência da API."""
    key:         str
    summary:     str
    description: dict        # ADF bruto — parseado em parsers.py
    status:      str
    issue_type:  str
    priority:    str
    assignee:    str
    reporter:    str
    created:     str         # ISO date YYYY-MM-DD
    updated:     str
    components:    list[str]
    labels:        list[str]
    versao_sistema: str
    url:           str


# ── Exceções próprias ─────────────────────────────────────────────────────────

class JiraClientError(Exception):
    """Erro base do cliente Jira."""


class JiraAuthError(JiraClientError):
    """Credenciais inválidas ou sem permissão."""


class JiraNotFoundError(JiraClientError):
    """Ticket não encontrado."""


class JiraConnectionError(JiraClientError):
    """Falha de conexão com o Jira."""


# ── Cliente ───────────────────────────────────────────────────────────────────

class JiraClient:
    """
    Cliente minimalista para a API REST v3 do Jira.
    Instanciar via JiraClient.from_config() para usar as credenciais do .env.
    """

    def __init__(self, base_url: str, email: str, token: str):
        self._base    = base_url.rstrip("/")
        self._auth    = HTTPBasicAuth(email, token)
        self._headers = {
            "Accept":       "application/json",
            "Content-Type": "application/json",
        }
        self._session = requests.Session()
        self._session.auth    = self._auth
        self._session.headers.update(self._headers)

    @classmethod
    def from_config(cls) -> "JiraClient":
        """Cria uma instância usando as credenciais do config.py."""
        return cls(
            base_url=config.JIRA_BASE_URL,
            email=config.JIRA_EMAIL,
            token=config.JIRA_API_TOKEN,
        )

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def get_issue(self, key: str) -> JiraIssue:
        """
        Busca um ticket pelo key (ex: AG-32021).
        Levanta exceções tipadas para cada caso de falha.
        """
        key = key.strip().upper()
        url = f"{self._base}/rest/api/3/issue/{key}"

        log.info("Buscando ticket %s...", key)

        try:
            resp = self._session.get(url, timeout=config.JIRA_TIMEOUT)
        except requests.ConnectionError as e:
            raise JiraConnectionError(
                f"Não foi possível conectar ao Jira: {self._base}\n"
                f"Verifique sua conexão e o JIRA_BASE_URL no .env.\n"
                f"Detalhe: {e}"
            ) from e
        except requests.Timeout:
            raise JiraConnectionError(
                f"Timeout ao conectar ao Jira (>{config.JIRA_TIMEOUT}s)."
            )

        self._raise_for_status(resp, key)

        data = resp.json()
        return self._parse_issue(data)

    def search_issues(self, jql: str, max_results: int = 20) -> list[JiraIssue]:
        """
        Busca issues via JQL.
        Ex: jql='project = AG AND status = "Em Andamento" AND assignee = currentUser()'
        """
        url  = f"{self._base}/rest/api/3/search"
        body = {
            "jql":        jql,
            "maxResults": max_results,
            "fields":     self._default_fields(),
        }

        log.info("Executando JQL: %s", jql)

        try:
            resp = self._session.post(url, json=body, timeout=config.JIRA_TIMEOUT)
        except requests.ConnectionError as e:
            raise JiraConnectionError(str(e)) from e

        self._raise_for_status(resp)

        issues = resp.json().get("issues", [])
        log.info("%d issue(s) encontrado(s).", len(issues))
        return [self._parse_issue(i) for i in issues]

    # ── Métodos privados ──────────────────────────────────────────────────────

    def _raise_for_status(self, resp: requests.Response, key: str = "") -> None:
        """Converte HTTP errors em exceções tipadas com mensagens claras."""
        if resp.status_code == 200:
            return
        if resp.status_code == 401:
            raise JiraAuthError(
                "Credenciais inválidas. Verifique JIRA_EMAIL e JIRA_API_TOKEN no .env.\n"
                "Gere um novo token em: https://id.atlassian.com/manage-profile/security/api-tokens"
            )
        if resp.status_code == 403:
            raise JiraAuthError(
                f"Sem permissão para acessar {'o ticket ' + key if key else 'este recurso'}."
            )
        if resp.status_code == 404:
            raise JiraNotFoundError(
                f"Ticket '{key}' não encontrado. Verifique a chave e o projeto."
            )
        # Outros erros HTTP
        try:
            detail = resp.json().get("errorMessages", [resp.text])[0]
        except Exception:
            detail = resp.text[:200]
        raise JiraClientError(f"Erro {resp.status_code} do Jira: {detail}")

    @staticmethod
    def _default_fields() -> list[str]:
        return [
            "summary", "description", "status", "issuetype",
            "priority", "assignee", "reporter", "created",
            "updated", "components", "labels",
        ]

    def _parse_issue(self, data: dict) -> JiraIssue:
        """Mapeia o JSON bruto da API para o dataclass JiraIssue."""
        f = data.get("fields", {})

        def safe(obj: dict | None, *keys: str, default: str = "") -> str:
            """Navega em dicionários aninhados com segurança."""
            for k in keys:
                if not isinstance(obj, dict):
                    return default
                obj = obj.get(k)  # type: ignore[assignment]
            return str(obj) if obj is not None else default

        created_raw = safe(f, "created")
        updated_raw = safe(f, "updated")

        return JiraIssue(
            key=data.get("key", ""),
            summary=safe(f, "summary"),
            description=f.get("description") or {},
            status=safe(f, "status", "name"),
            issue_type=safe(f, "issuetype", "name"),
            priority=safe(f, "priority", "name", default="Medium"),
            assignee=safe(f, "assignee", "displayName"),
            reporter=safe(f, "reporter", "displayName"),
            created=self._parse_date(created_raw),
            updated=self._parse_date(updated_raw),
            components=[c.get("name", "") for c in (f.get("components") or [])],
            labels=f.get("labels") or [],
            versao_sistema=self._extract_versao(f),
            url=f"{self._base}/browse/{data.get('key', '')}",
        )

    @staticmethod
    def _extract_versao(fields: dict) -> str:
        """
        Extrai a versão de entrega do ticket.
        Tenta customfield_10150 primeiro, depois fixVersions.
        Retorna apenas o número da versão (ex: '5.0.2604.xxxx').
        """
        for field in ("customfield_10150", "fixVersions"):
            versions = fields.get(field) or []
            if versions and isinstance(versions, list):
                name = versions[0].get("name", "")
                # Extrai apenas a parte da versão antes do primeiro espaço
                # "5.0.2604.xxxx - Lote 734 - Viasuper" → "5.0.2604.xxxx"
                return name.split(" - ")[0].strip() if name else ""
        return ""

    @staticmethod
    def _parse_date(raw: str) -> str:
        """Converte '2026-03-09T15:10:15.341-0300' → '2026-03-09'."""
        if not raw:
            return datetime.today().strftime("%Y-%m-%d")
        return raw[:10]