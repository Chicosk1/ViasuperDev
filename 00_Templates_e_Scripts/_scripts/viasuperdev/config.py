"""
config.py — Configuração centralizada do projeto.

Todas as variáveis de ambiente são lidas aqui.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

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

DEST_FOLDERS: dict[str, str] = {
    "ag":             "99_AGs/backlog",
    "processo":       "02_Processos",
    "regra-negocio":  "03_Regras_Negocio",
    "arquitetura":    "05_Arquiteturas",
    "padrao-tecnico": "04_Padroes_Tecnicos",
}

AG_STATUS_FOLDERS: dict[str, str] = {
    "backlog": "99_AGs/backlog",
    "doing":   "99_AGs/doing",
    "done":    "99_AGs/done",
}

ID_PREFIXES: dict[str, str] = {
    "ag":             "AG",
    "processo":       "PROC",
    "regra-negocio":  "RN",
    "arquitetura":    "ARQ",
    "padrao-tecnico": "PT",
}


# ── Templates ─────────────────────────────────────────────────────────────────

TEMPLATES_DIR: Path = _PROJECT_ROOT / "templates"


# ── Indexação (Fase 3 — RAG) ──────────────────────────────────────────────────

_chroma_raw = os.getenv("CHROMA_DIR", "")
CHROMA_DIR: Path = Path(_chroma_raw) if _chroma_raw else _PROJECT_ROOT / ".chroma"

# Provider padrão: huggingface (local, gratuito, PT-BR nativo)
# Para usar Voyage AI: EMBEDDINGS_PROVIDER=voyage no .env (requer VOYAGE_API_KEY)
# ATENÇÃO: trocar de provider exige reindexação completa (--full) em todas as coleções.
EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "huggingface")
EMBEDDINGS_MODEL: str    = os.getenv(
    "EMBEDDINGS_MODEL",
    "intfloat/multilingual-e5-small",  # 384d, PT-BR nativo, ~120 MB, MIT
)

# Voyage AI (legado — usado apenas se EMBEDDINGS_PROVIDER=voyage)
VOYAGE_API_KEY: str = os.getenv("VOYAGE_API_KEY", "")

# ── Source (Fase 3b — camada Delphi) ─────────────────────────────────────────
#
# Cada desenvolvedor aponta SOURCE_ROOT para a raiz do seu repositório Delphi.
# Exemplo no .env:
#   SOURCE_ROOT=C:/Projetos/Git_1
#
# O indexer vai varrer recursivamente SOURCE_ROOT procurando arquivos .pas,
# infere o módulo pela subpasta (SOURCE_ROOT/App/<Modulo>/arquivo.pas → Modulo)
# e persiste os chunks na coleção ChromaDB 'source'.
#
# Deixar SOURCE_ROOT vazio desativa a camada source sem erros —
# o comando `--only source` vai informar que a variável não está configurada.
_source_raw = os.getenv("SOURCE_ROOT", "")
SOURCE_ROOT: Path = Path(_source_raw) if _source_raw else Path()

INDEX_EXCLUDE_DIRS: set[str] = {
    "_scripts",
    "_templates",
    "_meta",
    ".obsidian",
    ".chroma",
    ".git",
    "node_modules",
}

INDEX_EXCLUDE_CONTEXTO_LLM: set[str] = {"baixo"}

TIPO_TO_COLECAO: dict[str, str] = {
    "ag":             "kb",
    "processo":       "kb",
    "regra-negocio":  "kb",
    "arquitetura":    "kb",
    "padrao-tecnico": "kb",
    "glossario":      "kb",
    "indice":         "kb",
}


# ── Validação na inicialização ────────────────────────────────────────────────

def validate() -> None:
    """
    Valida que as configurações obrigatórias estão presentes.
    Chamado no início de qualquer comando CLI.

    SOURCE_ROOT é opcional — só valida se o desenvolvedor configurou.
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

    # SOURCE_ROOT é opcional — valida apenas se foi configurado
    if _source_raw and not SOURCE_ROOT.exists():
        errors.append(
            f"SOURCE_ROOT configurado mas não encontrado: {SOURCE_ROOT}\n"
            "   Verifique se o caminho está correto ou remova SOURCE_ROOT do .env "
            "para desativar a camada source."
        )

    if errors:
        print("\n Erros de configuração encontrados:\n")
        for e in errors:
            print(f"   • {e}")
        print(f"\n   Verifique o arquivo: {_ENV_FILE}")
        print(f"   Exemplo disponível:  {_PROJECT_ROOT / '.env.example'}\n")
        sys.exit(1)