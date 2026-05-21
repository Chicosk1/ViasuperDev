"""
config.py — Configuração centralizada do projeto.

Todas as variáveis de ambiente são lidas aqui.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Estrutura esperada no vault:
# 00_Templates_e_Scripts/
# └── _scripts/
#     ├── .env                  ← credenciais (nunca commitar)
#     ├── .env.example
#     ├── pyproject.toml
#     ├── templates/            ← arquivos .j2
#     └── viasuperdev/
#         └── config.py        ← este arquivo
#
# __file__ = .../00_Templates_e_Scripts/_scripts/viasuperdev/config.py
# .parent  = .../00_Templates_e_Scripts/_scripts/viasuperdev/
# .parent.parent = .../00_Templates_e_Scripts/_scripts/   ← raiz do projeto

_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE     = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_FILE)


# ── Jira ──────────────────────────────────────────────────────────────────────

JIRA_BASE_URL: str  = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL: str     = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")
JIRA_TIMEOUT: int   = 15  # segundos


# ── Vault ─────────────────────────────────────────────────────────────────────

_vault_raw = os.getenv("VAULT_ROOT", "")
VAULT_ROOT: Path = Path(_vault_raw) if _vault_raw else Path.cwd()

# Mapeamento tipo de documento → pasta de destino dentro do vault
DEST_FOLDERS: dict[str, str] = {
    "ag":             "99_AGs/backlog",
    "processo":       "02_Processos",
    "regra-negocio":  "03_Regras_Negocio",
    "arquitetura":    "05_Arquiteturas",
    "padrao-tecnico": "04_Padroes_Tecnicos",
}

# Subpastas de status para AGs
AG_STATUS_FOLDERS: dict[str, str] = {
    "backlog": "99_AGs/backlog",
    "doing":   "99_AGs/doing",
    "done":    "99_AGs/done",
}

# Prefixos de ID por tipo (usado para auto-incremento)
ID_PREFIXES: dict[str, str] = {
    "ag":             "AG",
    "processo":       "PROC",
    "regra-negocio":  "RN",
    "arquitetura":    "ARQ",
    "padrao-tecnico": "PT",
}


# ── Templates ─────────────────────────────────────────────────────────────────

TEMPLATES_DIR: Path = _PROJECT_ROOT / "templates"


# ── Validação na inicialização ────────────────────────────────────────────────

def validate() -> None:
    """
    Valida que as configurações obrigatórias estão presentes.
    Chamado no início de qualquer comando CLI.
    """
    errors: list[str] = []

    if not JIRA_BASE_URL:
        errors.append("JIRA_BASE_URL não configurado no .env")
    if not JIRA_EMAIL:
        errors.append("JIRA_EMAIL não configurado no .env")
    if not JIRA_API_TOKEN:
        errors.append("JIRA_API_TOKEN não configurado no .env")
    if not _vault_raw:
        errors.append("VAULT_ROOT não configurado no .env")
    elif not VAULT_ROOT.exists():
        errors.append(f"VAULT_ROOT não encontrado: {VAULT_ROOT}")
    if not TEMPLATES_DIR.exists():
        errors.append(f"Pasta de templates não encontrada: {TEMPLATES_DIR}")

    if errors:
        print("\n Erros de configuração encontrados:\n")
        for e in errors:
            print(f"   • {e}")
        print(f"\n   Verifique o arquivo: {_ENV_FILE}")
        print(f"   Exemplo disponível:  {_PROJECT_ROOT / '.env.example'}\n")
        sys.exit(1)