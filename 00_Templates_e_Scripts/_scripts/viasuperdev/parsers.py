"""
parsers.py — Extração e transformação de dados do ADF Jira.

Responsabilidade única: transformar dados brutos do Jira em
estruturas limpas prontas para os templates Jinja2.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from viasuperdev.jira_client import JiraIssue

log = logging.getLogger(__name__)

# Prefixos de linha a ignorar na extração de conteúdo
_IGNORAR = ("»", "Descrição:", "Condição:", "Caminho:", "Módulo:")


# ── Modelos de saída ──────────────────────────────────────────────────────────

@dataclass
class ParsedAG:
    contexto:           str
    objetivo:           str
    escopo_inclui:      list[str]
    escopo_nao_inclui:  list[str]
    criterios:          list[str]
    referencias:        list[str]
    resultado_esperado: str
    modulo:             str
    prioridade:         str
    nome_rotina:        str = ""


@dataclass
class ParsedProcesso:
    objetivo:    str
    fluxo:       list[str]
    modulo:      str
    nome_rotina: str = ""


# ── Conversor ADF → texto ─────────────────────────────────────────────────────

def adf_to_text(node: dict | None) -> str:
    if not node:
        return ""
    ntype    = node.get("type", "")
    children = node.get("content", [])

    if ntype == "text":
        marks = {m["type"] for m in node.get("marks", [])}
        text  = node.get("text", "")
        if "strong" in marks: text = f"**{text}**"
        if "em"     in marks: text = f"*{text}*"
        if "code"   in marks: text = f"`{text}`"
        return text

    if ntype == "doc":
        return "".join(adf_to_text(c) for c in children)

    if ntype == "paragraph":
        inner = "".join(adf_to_text(c) for c in children).strip()
        return f"{inner}\n\n" if inner else ""

    if ntype == "heading":
        level = node.get("attrs", {}).get("level", 2)
        inner = "".join(adf_to_text(c) for c in children).strip()
        return f"{'#' * level} {inner}\n\n"

    if ntype == "bulletList":
        items = []
        for item in children:
            text = "".join(adf_to_text(c) for c in item.get("content", [])).strip()
            items.append(f"- {text}")
        return "\n".join(items) + "\n\n"

    if ntype == "orderedList":
        items = []
        for i, item in enumerate(children, 1):
            text = "".join(adf_to_text(c) for c in item.get("content", [])).strip()
            items.append(f"{i}. {text}")
        return "\n".join(items) + "\n\n"

    if ntype == "listItem":
        return "".join(adf_to_text(c) for c in children)

    if ntype == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        code = "".join(adf_to_text(c) for c in children)
        return f"```{lang}\n{code}\n```\n\n"

    if ntype == "blockquote":
        inner = "".join(adf_to_text(c) for c in children).strip()
        lines = "\n".join(f"> {l}" for l in inner.split("\n"))
        return f"{lines}\n\n"

    if ntype == "table":
        return _adf_table_to_md(node)

    if ntype == "hardBreak":
        return "\n"

    if ntype == "inlineCard":
        url = node.get("attrs", {}).get("url", "")
        return f"`{url}`" if url else ""

    return "".join(adf_to_text(c) for c in children)


def _adf_table_to_md(node: dict) -> str:
    rows: list[list[str]] = []
    for row in node.get("content", []):
        cells = []
        for cell in row.get("content", []):
            text = "".join(
                adf_to_text(c) for c in cell.get("content", [])
            ).strip().replace("\n", " ")
            cells.append(text)
        rows.append(cells)
    if not rows:
        return ""
    num_cols  = max(len(r) for r in rows)
    separator = "| " + " | ".join(["---"] * num_cols) + " |"
    lines     = []
    for i, row in enumerate(rows):
        padded = row + [""] * (num_cols - len(row))
        lines.append("| " + " | ".join(padded) + " |")
        if i == 0:
            lines.append(separator)
    return "\n".join(lines) + "\n\n"


def clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_md(text: str) -> str:
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    return re.sub(r"`([^`]+)`", r"\1", text).strip()


def _is_ignorable(line: str) -> bool:
    """Retorna True para linhas que não são conteúdo útil."""
    s = line.strip()
    return (
        not s
        or len(s) < 40
        or any(s.startswith(p) or p in s for p in ("»",))
        or any(s.startswith(p) for p in _IGNORAR)
        or s.startswith("#")
        or s.startswith("|")
    )


# ── Extratores ────────────────────────────────────────────────────────────────

def extract_criterios(text: str) -> list[str]:
    criterios: list[str] = []

    for m in re.finditer(
        r"(\d+\.\d+)\s*[-–:]\s*Crit[eé]rio[:\s]+([^\n]{5,120})", text
    ):
        criterios.append(f"{m.group(1)} — {_strip_md(m.group(2))}")
    if criterios:
        return criterios

    for m in re.finditer(r"^(\d+\.\d+)\s*[-–—]?\s*(.{10,120})", text, re.MULTILINE):
        item = _strip_md(m.group(2)).rstrip(".")
        if item:
            criterios.append(f"{m.group(1)} — {item}")
    if criterios:
        return criterios

    for m in re.finditer(r"[Ee]nt[ãa]o\s+(.{20,150}?)(?=\n|\Z)", text):
        item = _strip_md(m.group(1)).rstrip(".")
        if item and len(item) > 20:
            criterios.append(item[:150])

    return criterios or ["[ Extrair critérios manualmente do Jira ]"]


def extract_fluxo(text: str) -> list[str]:
    steps = []
    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"^\d+[\.\)]\s+.{10,}", line):
            steps.append(line)
    return steps or ["[ Detalhar fluxo após análise técnica ]"]


def resolve_modulo(issue: JiraIssue) -> str:
    """
    Resolve o módulo do ticket seguindo ordem de prioridade:

    1. customfield_10169 (campo 'Módulo' do Jira) — mais confiável,
       preenchido pelo analista diretamente no ticket.
       Ex: 'Nota Fiscal', 'Financeiro', 'Estoque'

    2. components — quando o projeto usa componentes para categorizar módulos.

    3. Breadcrumb do ADF — fallback via padrão 'Viasuper » ... » Módulo'
       extraído da descrição do ticket.

    4. 'Geral' — último recurso quando nenhuma fonte retorna valor.
    """
    # Prioridade 1: customfield_10169 via modulo_jira
    if issue.modulo_jira:
        return issue.modulo_jira

    # Prioridade 2: components
    if issue.components:
        return _strip_md(issue.components[0])

    # Prioridade 3: breadcrumb do ADF
    raw_text = adf_to_text(issue.description)
    segments = re.findall(r"»\s*([^»\n]{2,40}?)\s*(?=»|\n|$)", raw_text)
    if len(segments) >= 2:
        return _strip_md(segments[-2].strip())
    elif len(segments) == 1:
        return _strip_md(segments[0].strip())

    return "Geral"


def extract_nome_rotina(issue: JiraIssue) -> str:
    """
    Extrai o último segmento do breadcrumb como sugestão de nome da rotina.
    Ex: 'Viasuper » Processos » Nota » Nota Fiscal' → 'Nota Fiscal'
    Fallback: título do ticket.
    """
    raw_text = adf_to_text(issue.description)
    segments = re.findall(r"»\s*([^»\n]{2,60}?)\s*(?=»|\n|$)", raw_text)
    if segments:
        return segments[-1].strip()
    return issue.summary


def resolve_prioridade(jira_priority: str) -> str:
    return {
        "Highest": "alta", "High":   "alta",
        "Medium":  "media",
        "Low":     "baixa", "Lowest": "baixa",
    }.get(jira_priority, "media")


# ── Prompt interativo ─────────────────────────────────────────────────────────

def prompt_nome_rotina(sugestao: str) -> str:
    """
    Exibe a sugestão extraída do breadcrumb e permite confirmação ou edição.
    Retorna o nome escolhido pelo usuário.
    """
    print(f"\n{'─' * 50}")
    print(f"  Nome da rotina sugerido: \"{sugestao}\"")
    print(f"  (extraído do breadcrumb do Jira)")
    resposta = input(f"  Confirmar ou digitar novo nome [Enter para confirmar]: ").strip()
    print(f"{'─' * 50}\n")
    return resposta if resposta else sugestao


# ── Parsers de alto nível ─────────────────────────────────────────────────────

def parse_ag(issue: JiraIssue, nome_rotina: str = "") -> ParsedAG:
    raw   = clean(adf_to_text(issue.description))
    lines = [l.strip() for l in raw.split("\n") if not _is_ignorable(l)]

    context_lines = [_strip_md(l) for l in lines][:3]
    contexto = " ".join(context_lines)[:600] if context_lines else (
        "[ Descrever o contexto atual e o problema que gerou esta AG ]"
    )

    objetivo = ""
    for line in lines:
        if any(k in line.lower() for k in ["posso ", "permite ", "objetivo", "finalidade"]):
            clean_line = _strip_md(line)
            if len(clean_line) > 600:
                last_dot = clean_line[:600].rfind(".")
                clean_line = clean_line[:last_dot + 1] if last_dot > 0 else clean_line[:600]
            objetivo = clean_line
            break
    if not objetivo:
        joined = " ".join(lines)[:600]
        last_dot = joined.rfind(".")
        objetivo = joined[:last_dot + 1] if last_dot > 100 else joined
        objetivo = _strip_md(objetivo) if objetivo else "[ Descrever o objetivo da AG ]"

    return ParsedAG(
        contexto=contexto,
        objetivo=objetivo,
        escopo_inclui=["[ Definir escopo após análise — use os critérios do Jira como base ]"],
        escopo_nao_inclui=["[ Definir explicitamente o que não deve ser tocado nesta AG ]"],
        criterios=extract_criterios(raw),
        referencias=["[ Linkar processos, RNs e arquiteturas relacionadas após análise ]"],
        resultado_esperado="[ Descrever o artefato de saída: método, unit, tabela, tela, etc. ]",
        modulo=resolve_modulo(issue),
        prioridade=resolve_prioridade(issue.priority),
        nome_rotina=nome_rotina,
    )


def parse_processo(issue: JiraIssue, nome_rotina: str = "") -> ParsedProcesso:
    raw   = clean(adf_to_text(issue.description))
    lines = [l.strip() for l in raw.split("\n") if not _is_ignorable(l)]

    objetivo_raw = " ".join(lines)[:600]
    last_dot     = objetivo_raw.rfind(".")
    objetivo     = _strip_md(
        objetivo_raw[:last_dot + 1] if last_dot > 80 else objetivo_raw
    ) if objetivo_raw else "[ Descrever o objetivo do processo ]"

    return ParsedProcesso(
        objetivo=objetivo,
        fluxo=extract_fluxo(raw),
        modulo=resolve_modulo(issue),
        nome_rotina=nome_rotina,
    )