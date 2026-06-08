#!/usr/bin/env python3
"""
init_viasuperdev.py -- ViasuperDev environment initialization and status check.

Usage:
  python init_viasuperdev.py --check
      Returns JSON with initialization status, vault stats and ChromaDB stats.

  python init_viasuperdev.py --setup <workspace_path>
      Verifies vault, ChromaDB, scripts. Returns JSON report.

  python init_viasuperdev.py --configure-permissions
      Configures Claude Code permissions in ~/.claude/settings.json.

  python init_viasuperdev.py --complete
      Marks environment as initialized. Creates .claude/tasks/ state dir.

  python init_viasuperdev.py --reset
      Marks environment as not initialized (forces re-init on next run).

  python init_viasuperdev.py --init-ag AG-XXXXX
      Creates .claude/tasks/AG-XXXXX/branch-state.json with all fields
      initialized. If the file already exists, returns current state without
      overwriting (status: JA_EXISTE).
      Returns JSON: {status: "CRIADO"|"JA_EXISTE"|"ERRO", state: {...}, path: str}.

  python init_viasuperdev.py --update-state AG-XXXXX <key> <value>
      Updates a single field in branch-state.json without touching other fields.
      Value is parsed as JSON (so pass true/false/null/numbers unquoted,
      strings in double quotes).
      Example: --update-state AG-31945 etapa_atual '"investigacao"'
      Example: --update-state AG-31945 worktree_criado true
      Returns JSON: {status: "OK"|"ERRO", field: str, value: any}.

  python init_viasuperdev.py --pr-url AG-XXXXX
      Builds the Bitbucket PR URL for the AG from branch-state.json and config.
      Returns JSON: {status: "OK"|"ERRO", url: str, branch: str}.

  python init_viasuperdev.py --worktree AG-XXXXX [--branch <branch>]
      Creates a git worktree for the AG at <SOURCE_ROOT>/../worktrees/AG-XXXXX.
      Creates branch feature/AG-XXXXX (or bugfix/ if title contains "bug"/"fix").
      Returns JSON: {worktree_path, branch, status}.

  python init_viasuperdev.py --check-worktree AG-XXXXX
      Checks if worktree for AG still exists.
      Returns JSON: {worktree_ok: bool, worktree_path: str|null}.

  python init_viasuperdev.py --remove-worktree AG-XXXXX
      Removes worktree for AG (after PR merge). Keeps branch for safety.
      Returns JSON: {status: "OK"|"NOT_FOUND"|"ERRO", detail: str}.

  python init_viasuperdev.py --save-file <path> [--encoding <enc>]
      Writes stdin content to <path> with specified encoding (default utf-8).
      Used by skill to save generated Delphi code to worktree.
      Returns JSON: {status: "OK"|"ERRO", path: str}.

  python init_viasuperdev.py --set-vault <vault_root>
      Saves vault_root and derived scripts_dir to ~/.claude/viasuperdev-config.json.
      Called on first run to make the project root path configurable per developer.
      Returns JSON: {status: "OK"|"ERRO", vault_root: str, scripts_dir: str}.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

CONFIG_PATH   = Path.home() / ".claude" / "viasuperdev-config.json"
STATE_DIR_REL = ".claude/tasks"   # relative to workspace root

# Localizacao do script:
#   <vault_root>/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py
#
# SKILL_BASE      = _scripts/viasuperdev/
# SCRIPTS_DIR     = _scripts/
# VIASUPERDEV_DIR = vault_root  (raiz do repositorio — contem vault + scripts)
# WORKSPACE       = raiz do repo git (igual a VIASUPERDEV_DIR) — confirmado via git

SKILL_BASE      = Path(__file__).parent            # _scripts/viasuperdev/
SCRIPTS_DIR     = SKILL_BASE.parent                # _scripts/
VIASUPERDEV_DIR = SKILL_BASE.parent.parent.parent  # vault_root (ex: viasuper-docs/)

CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
REQUIRED_PERMISSIONS_ALLOW = ["Read(*)", "Edit(*)", "Write(*)", "Bash(*)", "Agent(*)"]

# vault_search.py mora no mesmo pacote viasuperdev/
# init_viasuperdev.py nao verifica a si mesmo
REQUIRED_SCRIPTS = [
    "viasuperdev/vault_search.py",
]

# Bitbucket — configuravel via --setup, lido do config em runtime
BITBUCKET_WORKSPACE_DEFAULT = "viasoftnimitz"
BITBUCKET_REPO_DEFAULT      = "viasuper-mercado"
BITBUCKET_DEST_BRANCH       = "main"

# Schema inicial do branch-state.json
_BRANCH_STATE_SCHEMA: dict = {
    "ticket":          "",
    "fase_atual":      1,
    "etapa_atual":     "leitura-ag",
    "worktree_criado": False,
    "worktree_path":   None,
    "branch":          None,
    "chunks_coletados": [],
    "gaps_contexto":   [],
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _out(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _workspace_root() -> Path:
    """
    Retorna a raiz do repositorio git (ClaudeCopilot/).
    Usa git rev-parse como fonte de verdade.
    Fallback: pai do VIASUPERDEV_DIR.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10, cwd=str(SKILL_BASE),
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    # Fallback: ClaudeCopilot/ = pai de ViasuperDev/
    return VIASUPERDEV_DIR.parent


def _viasuperdev_dir() -> Path:
    """
    Retorna o diretorio ViasuperDev/ dentro do repositorio.
    Usa VIASUPERDEV_DIR como fonte de verdade (derivado do path do script).
    """
    return VIASUPERDEV_DIR


def _load_viasuperdev_config() -> tuple[Path | None, Path | None, Path | None]:
    """Loads VAULT_ROOT, CHROMA_DIR, SOURCE_ROOT from .env file in _scripts/."""
    # .env mora em SCRIPTS_DIR (_scripts/), um nivel acima do pacote viasuperdev/
    env_file = SCRIPTS_DIR / ".env"
    vault, chroma, source = None, None, None

    if not env_file.exists():
        return vault, chroma, source

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not val:
            continue
        if key == "VAULT_ROOT":
            vault = Path(val)
        elif key == "CHROMA_DIR":
            chroma = Path(val)
        elif key == "SOURCE_ROOT":
            source = Path(val)

    return vault, chroma, source


def _chroma_stats(chroma_dir: Path) -> dict:
    """Returns chunk counts per collection from ChromaDB manifests."""
    stats: dict[str, int] = {}
    for manifest_name, collection in [
        ("manifest_kb.json", "knowledge_base"),
        ("manifest_source.json", "source"),
    ]:
        manifest_path = chroma_dir / manifest_name
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                stats[collection] = len(manifest)
            except Exception:
                stats[collection] = -1
        else:
            stats[collection] = 0
    return stats


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_check() -> None:
    cfg    = load_config()
    vault, chroma, source = _load_viasuperdev_config()
    vsd    = _viasuperdev_dir()   # ViasuperDev/

    result: dict = {
        "initialized":     cfg.get("initialized", False),
        "viasuperdev_dir": str(vsd),
        "scripts_dir":     str(SCRIPTS_DIR),
        "vault_root":      str(vault)  if vault  else "NAO_CONFIGURADO",
        "vault_exists":    vault.exists()  if vault  else False,
        "chroma_dir":      str(chroma) if chroma else "NAO_CONFIGURADO",
        "chroma_exists":   chroma.exists() if chroma else False,
        "source_root":     str(source) if source else "NAO_CONFIGURADO",
        "source_exists":   source.exists() if source else False,
        "index_kb_ok":     False,
        "index_source_ok": False,
        "vault_stats":     {},
        "chroma_stats":    {},
    }

    # Vault stats
    if vault and vault.exists():
        md_files = list(vault.rglob("*.md"))
        by_type: dict[str, int] = {}
        for f in md_files:
            stem = f.stem.upper()
            for prefix in ["RN", "PROC", "PT", "ARQ", "GLOS", "IDX", "AG"]:
                if stem.startswith(prefix + "-") or stem.startswith(prefix):
                    by_type[prefix] = by_type.get(prefix, 0) + 1
                    break
        result["vault_stats"] = {"total": len(md_files), "by_type": by_type}

    # ChromaDB stats
    if chroma and chroma.exists():
        stats = _chroma_stats(chroma)
        result["chroma_stats"] = stats
        result["index_kb_ok"]     = stats.get("knowledge_base", 0) > 0
        result["index_source_ok"] = stats.get("source", 0) > 0

    _out(result)


def cmd_configure_permissions() -> None:
    settings_path = CLAUDE_SETTINGS_PATH
    settings: dict = {}

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    existing = set(settings.get("permissions", {}).get("allow", []))
    added = []
    for perm in REQUIRED_PERMISSIONS_ALLOW:
        if perm not in existing:
            existing.add(perm)
            added.append(perm)

    if "permissions" not in settings:
        settings["permissions"] = {}
    settings["permissions"]["allow"] = sorted(existing)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")

    _out({"status": "OK", "added": added, "already_present": [p for p in REQUIRED_PERMISSIONS_ALLOW if p not in added]})


def cmd_setup(workspace_path: str) -> None:
    ws = Path(workspace_path)
    # init_viasuperdev.py mora em _scripts/viasuperdev/ junto com os demais modulos
    scripts_dir = SCRIPTS_DIR
    vault, chroma, source = _load_viasuperdev_config()

    issues = []
    report: dict = {
        "workspace":     str(ws),
        "vault_root":    str(vault)  if vault  else "AUSENTE",
        "chroma_dir":    str(chroma) if chroma else "AUSENTE",
        "source_root":   str(source) if source else "AUSENTE (opcional)",
        "scripts_ok":    True,
        "missing_scripts": [],
    }

    if not vault or not vault.exists():
        issues.append("VAULT_ROOT invalido ou nao encontrado")
    if not chroma:
        issues.append("CHROMA_DIR nao configurado no .env")

    # Verifica scripts — vault_search.py em viasuperdev/
    missing = []
    for script in REQUIRED_SCRIPTS:
        if not (scripts_dir / script).exists():
            missing.append(script)
    if missing:
        report["scripts_ok"] = False
        report["missing_scripts"] = missing

    report["issues"] = issues

    # Salva configuracoes Bitbucket no config pessoal para uso pelo --pr-url
    cfg = load_config()
    cfg.setdefault("bitbucket_workspace", BITBUCKET_WORKSPACE_DEFAULT)
    cfg.setdefault("bitbucket_repo",      BITBUCKET_REPO_DEFAULT)
    cfg.setdefault("bitbucket_dest",      BITBUCKET_DEST_BRANCH)
    save_config(cfg)

    _out(report)


def cmd_complete() -> None:
    vsd       = _viasuperdev_dir()
    state_dir = vsd / STATE_DIR_REL
    state_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    cfg["initialized"] = True
    cfg["workspace"]   = str(_workspace_root())
    cfg.setdefault("vault_root",  str(VIASUPERDEV_DIR))
    cfg.setdefault("scripts_dir", str(SCRIPTS_DIR))
    save_config(cfg)

    _out({"status": "OK", "state_dir": str(state_dir), "config": str(CONFIG_PATH),
          "vault_root": cfg["vault_root"], "scripts_dir": cfg["scripts_dir"]})


def cmd_reset() -> None:
    cfg = load_config()
    cfg["initialized"] = False
    save_config(cfg)
    _out({"status": "OK", "initialized": False})


def cmd_init_ag(ticket: str) -> None:
    """
    Creates branch-state.json for the AG with all fields initialized.
    If the file already exists, returns current state without overwriting.
    """
    if not ticket:
        _out({"status": "ERRO", "detail": "Ticket nao informado"})
        return

    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"

    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            _out({"status": "JA_EXISTE", "state": state, "path": str(state_file)})
        except Exception as e:
            _out({"status": "ERRO", "detail": f"branch-state.json corrompido: {e}"})
        return

    state = dict(_BRANCH_STATE_SCHEMA)
    state["ticket"] = ticket

    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        _out({"status": "CRIADO", "state": state, "path": str(state_file)})
    except Exception as e:
        _out({"status": "ERRO", "detail": str(e)})


def cmd_update_state(ticket: str, key: str, raw_value: str) -> None:
    """
    Updates a single field in branch-state.json.
    raw_value is parsed as JSON: true/false/null/numbers unquoted, strings in double quotes.
    """
    if not ticket or not key:
        _out({"status": "ERRO", "detail": "Ticket e key sao obrigatorios"})
        return

    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"

    if not state_file.exists():
        _out({"status": "ERRO", "detail": f"branch-state.json nao encontrado para {ticket}. Execute --init-ag primeiro."})
        return

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        _out({"status": "ERRO", "detail": f"branch-state.json corrompido: {e}"})
        return

    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        # Se nao for JSON valido, trata como string literal
        value = raw_value

    state[key] = value
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    _out({"status": "OK", "field": key, "value": value, "path": str(state_file)})


def cmd_pr_url(ticket: str) -> None:
    """
    Builds the Bitbucket PR URL for the AG from branch-state.json and config.
    """
    if not ticket:
        _out({"status": "ERRO", "detail": "Ticket nao informado"})
        return

    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"

    if not state_file.exists():
        _out({"status": "ERRO", "detail": f"branch-state.json nao encontrado para {ticket}. Execute --init-ag primeiro."})
        return

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        _out({"status": "ERRO", "detail": f"branch-state.json corrompido: {e}"})
        return

    branch = state.get("branch")
    if not branch:
        _out({"status": "ERRO", "detail": "Branch nao registrada no branch-state.json. Execute --worktree primeiro."})
        return

    # Le workspace e repo do config pessoal (salvo pelo --setup); usa defaults como fallback
    cfg       = load_config()
    workspace = cfg.get("bitbucket_workspace", BITBUCKET_WORKSPACE_DEFAULT)
    repo      = cfg.get("bitbucket_repo",      BITBUCKET_REPO_DEFAULT)
    dest      = cfg.get("bitbucket_dest",      BITBUCKET_DEST_BRANCH)

    url = (
        f"https://bitbucket.org/{workspace}/{repo}/pull-requests/new"
        f"?source={branch}&dest={dest}"
    )
    _out({"status": "OK", "url": url, "branch": branch, "dest": dest})


def cmd_worktree(ticket: str, branch_override: str | None = None) -> None:
    """Creates a git worktree for the AG."""
    _, _, source = _load_viasuperdev_config()
    if not source or not source.exists():
        _out({"status": "ERRO", "detail": "SOURCE_ROOT nao configurado ou inexistente"})
        return

    # Determine branch name
    if branch_override:
        branch = branch_override
    else:
        # Simple heuristic: bugfix if ticket contains common bug keywords
        branch_type = "feature"
        branch = f"{branch_type}/{ticket}"

    worktrees_dir = source.parent / "worktrees"
    worktrees_dir.mkdir(parents=True, exist_ok=True)
    worktree_path = worktrees_dir / ticket

    if worktree_path.exists():
        _out({"status": "ALREADY_EXISTS", "worktree_path": str(worktree_path), "branch": branch})
        return

    # Create branch and worktree
    try:
        # Create branch from main
        subprocess.run(
            ["git", "-C", str(source), "branch", branch, "main"],
            capture_output=True, text=True, check=False,
        )
        # Create worktree
        result = subprocess.run(
            ["git", "-C", str(source), "worktree", "add", str(worktree_path), branch],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            _out({"status": "ERRO", "detail": result.stderr.strip()})
            return
    except Exception as e:
        _out({"status": "ERRO", "detail": str(e)})
        return

    # Update branch-state.json
    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    else:
        state = {"ticket": ticket, "fase_atual": 2}

    state["worktree_criado"] = True
    state["worktree_path"]   = str(worktree_path)
    state["branch"]          = branch
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    _out({"status": "OK", "worktree_path": str(worktree_path), "branch": branch})


def cmd_check_worktree(ticket: str) -> None:
    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"

    if not state_file.exists():
        _out({"worktree_ok": False, "worktree_path": None, "detail": "branch-state.json nao encontrado"})
        return

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        _out({"worktree_ok": False, "worktree_path": None, "detail": "branch-state.json corrompido"})
        return

    wt_path = state.get("worktree_path")
    if wt_path and Path(wt_path).exists():
        _out({"worktree_ok": True, "worktree_path": wt_path, "branch": state.get("branch")})
    else:
        _out({"worktree_ok": False, "worktree_path": wt_path, "detail": "worktree nao encontrado no disco"})


def cmd_remove_worktree(ticket: str) -> None:
    vsd        = _viasuperdev_dir()
    state_file = vsd / STATE_DIR_REL / ticket / "branch-state.json"

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        wt_path = state.get("worktree_path")
        if not wt_path:
            _out({"status": "NOT_FOUND", "detail": "worktree_path nao registrado"})
            return

        _, _, source = _load_viasuperdev_config()
        result = subprocess.run(
            ["git", "-C", str(source), "worktree", "remove", wt_path, "--force"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            _out({"status": "ERRO", "detail": result.stderr.strip()})
            return

        state["worktree_criado"] = False
        state["worktree_path"]   = None
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        _out({"status": "OK", "removed": wt_path})

    except FileNotFoundError:
        _out({"status": "NOT_FOUND", "detail": "branch-state.json nao encontrado"})
    except Exception as e:
        _out({"status": "ERRO", "detail": str(e)})


def cmd_set_vault(vault_root_str: str) -> None:
    """
    Saves vault_root and derived scripts_dir to ~/.claude/viasuperdev-config.json.
    Called on first run to make the project root path configurable per developer.
    """
    vault = Path(vault_root_str)
    if not vault.exists():
        _out({"status": "ERRO", "detail": f"Caminho nao encontrado: {vault}"})
        return

    scripts = vault / "00_Templates_e_Scripts" / "_scripts"
    if not scripts.exists():
        _out({
            "status": "ERRO",
            "detail": (
                f"Pasta _scripts nao encontrada em {scripts}. "
                "Confirme que o caminho informado e a raiz do repositorio viasuper-docs."
            ),
        })
        return

    cfg = load_config()
    cfg["vault_root"]  = str(vault)
    cfg["scripts_dir"] = str(scripts)
    save_config(cfg)

    _out({
        "status":      "OK",
        "vault_root":  str(vault),
        "scripts_dir": str(scripts),
        "config":      str(CONFIG_PATH),
    })


def cmd_save_file(path: str, encoding: str = "utf-8") -> None:
    """Writes stdin content to <path> with given encoding."""
    try:
        content = sys.stdin.read()
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=encoding)
        _out({"status": "OK", "path": str(target), "bytes": len(content.encode(encoding))})
    except Exception as e:
        _out({"status": "ERRO", "detail": str(e)})


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if "--check" in args and "--check-worktree" not in args:
        cmd_check()

    elif "--configure-permissions" in args:
        cmd_configure_permissions()

    elif "--setup" in args:
        idx = args.index("--setup")
        ws_path = args[idx + 1] if idx + 1 < len(args) else str(Path.cwd())
        cmd_setup(ws_path)

    elif "--complete" in args:
        cmd_complete()

    elif "--reset" in args:
        cmd_reset()

    elif "--init-ag" in args:
        idx = args.index("--init-ag")
        ticket = args[idx + 1] if idx + 1 < len(args) else ""
        cmd_init_ag(ticket)

    elif "--update-state" in args:
        idx = args.index("--update-state")
        ticket    = args[idx + 1] if idx + 1 < len(args) else ""
        key       = args[idx + 2] if idx + 2 < len(args) else ""
        raw_value = args[idx + 3] if idx + 3 < len(args) else "null"
        cmd_update_state(ticket, key, raw_value)

    elif "--pr-url" in args:
        idx = args.index("--pr-url")
        ticket = args[idx + 1] if idx + 1 < len(args) else ""
        cmd_pr_url(ticket)

    elif "--worktree" in args:
        idx = args.index("--worktree")
        ticket = args[idx + 1] if idx + 1 < len(args) else ""
        branch = None
        if "--branch" in args:
            bidx = args.index("--branch")
            branch = args[bidx + 1] if bidx + 1 < len(args) else None
        cmd_worktree(ticket, branch)

    elif "--check-worktree" in args:
        idx = args.index("--check-worktree")
        ticket = args[idx + 1] if idx + 1 < len(args) else ""
        cmd_check_worktree(ticket)

    elif "--remove-worktree" in args:
        idx = args.index("--remove-worktree")
        ticket = args[idx + 1] if idx + 1 < len(args) else ""
        cmd_remove_worktree(ticket)

    elif "--save-file" in args:
        idx = args.index("--save-file")
        path = args[idx + 1] if idx + 1 < len(args) else ""
        enc = "utf-8"
        if "--encoding" in args:
            eidx = args.index("--encoding")
            enc = args[eidx + 1] if eidx + 1 < len(args) else "utf-8"
        cmd_save_file(path, enc)

    elif "--set-vault" in args:
        idx = args.index("--set-vault")
        vault_path = args[idx + 1] if idx + 1 < len(args) else ""
        if not vault_path:
            _out({"status": "ERRO", "detail": "Informe o caminho da raiz do repositorio. Ex: --set-vault C:/Repositorios/viasuper-docs"})
        else:
            cmd_set_vault(vault_path)

    else:
        print(__doc__)
        sys.exit(1)