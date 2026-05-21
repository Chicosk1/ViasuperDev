"""
vault_writer.py — Escrita de documentos no vault Obsidian.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from viasuperdev import config
from viasuperdev.jira_client import JiraIssue
from viasuperdev.parsers import ParsedAG, ParsedProcesso

log   = logging.getLogger(__name__)
TODAY = date.today().isoformat()


# ── Motor de templates ────────────────────────────────────────────────────────

def _get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(template_name: str, variables: dict) -> str:
    return _get_jinja_env().get_template(template_name).render(**variables)


# ── Utilitários ───────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.lower()
    for src, dst in {
        "à":"a","á":"a","â":"a","ã":"a","ä":"a",
        "è":"e","é":"e","ê":"e","ë":"e",
        "ì":"i","í":"i","î":"i","ï":"i",
        "ò":"o","ó":"o","ô":"o","õ":"o","ö":"o",
        "ù":"u","ú":"u","û":"u","ü":"u",
        "ç":"c","ñ":"n",
    }.items():
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9\s\-]", "", text)
    text = re.sub(r"[\s\-]+", "-", text).strip("-")
    return text[:70]


def next_id(folder: Path, prefix: str) -> str:
    pattern     = re.compile(rf"{re.escape(prefix)}-(\d+)", re.IGNORECASE)
    existing_ids = [
        int(m.group(1))
        for f in folder.rglob("*.md")
        if (m := pattern.search(f.stem))
    ]
    return f"{prefix}-{max(existing_ids) + 1 if existing_ids else 1:03d}"


def _next_version(content: str) -> str:
    """
    Lê o maior número de versão no §7 Histórico e retorna o próximo.
    Ex: se existir '1.2', retorna '1.3'. Se só houver '1.0', retorna '1.1'.
    """
    versions = re.findall(r"\|\s*[\d-]+\s*\|\s*(\d+)\.(\d+)\s*\|", content)
    if not versions:
        return "1.1"
    major, minor = max((int(ma), int(mi)) for ma, mi in versions)
    return f"{major}.{minor + 1}"


# ── Escritores ────────────────────────────────────────────────────────────────

def write_ag(issue: JiraIssue, parsed: ParsedAG, dry_run: bool = False) -> Path:
    dest_folder = config.VAULT_ROOT / config.DEST_FOLDERS["ag"]
    filename    = f"{issue.key}-{slugify(parsed.nome_rotina or issue.summary)}.md"
    content     = render("ag.j2", {"issue": issue, "parsed": parsed, "today": TODAY})
    return _write_file(dest_folder, filename, content, dry_run)


def write_processo(
    issue:   JiraIssue,
    parsed:  ParsedProcesso,
    dry_run: bool = False,
) -> Path:
    dest_folder = config.VAULT_ROOT / config.DEST_FOLDERS["processo"]
    prefix      = config.ID_PREFIXES["processo"]
    doc_id      = next_id(dest_folder, prefix)
    filename    = f"{doc_id}-{slugify(parsed.nome_rotina or issue.summary)}.md"
    content     = render("processo.j2", {
        "issue": issue, "parsed": parsed, "doc_id": doc_id, "today": TODAY,
    })
    return _write_file(dest_folder, filename, content, dry_run)


# ── Atualização de processo existente ────────────────────────────────────────

def find_processo(doc_id: str) -> Path:
    folder  = config.VAULT_ROOT / config.DEST_FOLDERS["processo"]
    matches = list(folder.rglob(f"{doc_id.upper()}-*.md"))
    if not matches:
        existing = [f.stem for f in folder.rglob("*.md")]
        raise FileNotFoundError(
            f"Processo '{doc_id}' não encontrado em {folder}\n"
            f"  Existentes: {existing if existing else '(nenhum)'}"
        )
    if len(matches) > 1:
        log.warning("Múltiplos arquivos para %s: %s", doc_id, matches)
    return matches[0]


def merge_processo(
    existing_path: Path,
    issue:         JiraIssue,
    parsed:        ParsedProcesso,
    dry_run:       bool = False,
) -> Path:
    """
    Faz merge de uma nova AG em um processo existente.
    Acrescenta — nunca sobrescreve conteúdo existente.
    """
    content = existing_path.read_text(encoding="utf-8")

    # 1. Atualiza data_revisao
    content = re.sub(r"data_revisao: [\d-]+", f"data_revisao: {TODAY}", content)

    # 2. Acrescenta referência à nova AG no campo jira
    new_ref = issue.url
    if "jira:\n  -" in content:
        content = content.replace("jira:\n  -", f'jira:\n  - "{new_ref}"\n  -', 1)
    else:
        content = re.sub(
            r'jira: "([^"]+)"',
            f'jira:\n  - "\\1"\n  - "{new_ref}"',
            content,
        )

    # 3. Acrescenta passos novos no fluxo
    placeholder = "[ Detalhar fluxo após análise técnica ]"
    if parsed.fluxo and parsed.fluxo != [placeholder]:
        existing_steps = set(re.findall(r"^\d+\.\s+(.+)$", content, re.MULTILINE))
        new_steps = [
            step for step in parsed.fluxo
            if re.sub(r"^\d+\.\s+", "", step).strip() not in existing_steps
        ]
        if new_steps:
            existing_nums = [int(n) for n in re.findall(r"^(\d+)\.", content, re.MULTILINE)]
            next_num      = max(existing_nums) + 1 if existing_nums else 1
            renumbered    = [
                f"{next_num + i}. {re.sub(r'^\\d+\\.\\s+', '', s)}"
                for i, s in enumerate(new_steps)
            ]
            content = re.sub(
                r"(## 5\. Componentes Técnicos)",
                "\n".join(renumbered) + "\n\n\\1",
                content,
            )
            log.info("Adicionados %d novo(s) passo(s) ao fluxo.", len(renumbered))

    # 4. Próxima versão incremental (1.0 → 1.1 → 1.2...)
    next_ver      = _next_version(content)
    summary_short = issue.summary[:60]
    history_entry = (
        f"| {TODAY} | {next_ver} | "
        f"Merge com [{issue.key}]({issue.url}) — {summary_short} |"
    )

    if "## 7. Histórico" in content:
        content = re.sub(
            r"(\|[-]+\|[-]+\|[-]+\|\n)",
            rf"\1{history_entry}\n",
            content,
        )
    else:
        content += (
            "\n## 7. Histórico\n\n"
            "| Data | Versão | Descrição |\n"
            "|---|---|---|\n"
            f"{history_entry}\n"
        )

    # 5. Exibe ou salva
    if dry_run:
        print(f"\n{'=' * 60}\n[DRY RUN] Atualizando: {existing_path}\n{'=' * 60}")
        print(content)
        return existing_path

    existing_path.write_text(content, encoding="utf-8")
    log.info("Processo atualizado: %s", existing_path)
    return existing_path


# ── Escrita de arquivo ────────────────────────────────────────────────────────

def _write_file(folder: Path, filename: str, content: str, dry_run: bool) -> Path:
    output_path = folder / filename

    if dry_run:
        print(f"\n{'=' * 60}\n[DRY RUN] {output_path}\n{'=' * 60}")
        print(content)
        log.info("Dry run — arquivo não salvo.")
        return output_path

    if output_path.exists():
        log.warning("Arquivo já existe: %s", output_path)
        if input("Sobrescrever? (s/N): ").strip().lower() != "s":
            raise FileExistsError(f"Arquivo já existe: {output_path}")

    folder.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    log.info("Arquivo criado: %s", output_path)
    return output_path