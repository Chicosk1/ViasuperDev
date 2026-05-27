"""
vault_search.py — Busca direta no vault do ViasuperDev.

Usado como fallback quando o ChromaDB retorna score < 0.75.
Varre os arquivos Markdown do vault por termos, IDs de documentos
e analise de impacto entre AGs e documentos de referencia.

Uso:
  python vault_search.py <termo>
  python vault_search.py <termo> --section regras-negocio
  python vault_search.py --id RN-004
  python vault_search.py --id PROC-001
  python vault_search.py --list
  python vault_search.py --impact AG-XXXXX

Exemplos:
  python vault_search.py "rateio proporcional IBS"
  python vault_search.py "base complementar" --section regras-negocio
  python vault_search.py --id RN-004
  python vault_search.py --impact AG-31945
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# Garante saida UTF-8 no terminal Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ── Configuracao ──────────────────────────────────────────────────────────────

def _workspace() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return os.getcwd()


def _vault_root() -> Path:
    """Le VAULT_ROOT do .env do projeto; fallback para raiz do workspace."""
    ws = _workspace()
    env_file = Path(ws) / "00_Templates_e_Scripts" / "_scripts" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("VAULT_ROOT="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                p = Path(val)
                if p.exists():
                    return p
    return Path(ws)


VAULT = _vault_root()

# Pastas do vault mapeadas por tipo de documento
VAULT_FOLDERS: dict[str, str] = {
    "indice":         "01_Indices",
    "processo":       "02_Processos",
    "regra-negocio":  "03_Regras_Negocio",
    "padrao-tecnico": "04_Padroes_Tecnicos",
    "arquitetura":    "05_Arquiteturas",
    "glossario":      "06_Glossarios",
    "ag":             "99_AGs",
}

# Prefixos de ID por tipo
ID_PREFIXES: dict[str, str] = {
    "RN":   "03_Regras_Negocio",
    "PROC": "02_Processos",
    "PT":   "04_Padroes_Tecnicos",
    "ARQ":  "05_Arquiteturas",
    "AG":   "99_AGs",
}

# Secoes padrao dos documentos do vault (H2)
SECTIONS: dict[str, str] = {
    "definicao":        "## 1. Definição",
    "contexto":         "## 2. Contexto",
    "regras-negocio":   "## 3. Condição (Se / Então)",
    "exemplos":         "## 4. Exemplos",
    "excecoes":         "## 5. Exceções",
    "parametros":       "## 6. Parâmetros do ERP",
    "historico":        "## 7. Histórico",
    # AG
    "objetivo":         "## 2. Objetivo",
    "escopo":           "## 3. Escopo",
    "criterios":        "## 4. Critérios de Aceite",
    "dod":              "## 5. Definição de Pronto",
    "referencias":      "## 6. Referências Técnicas",
    "resultado":        "## 7. Resultado Esperado",
}

# Padroes de artefatos tecnicos Delphi
_ARTIFACT_PATTERNS = [
    r'\b([A-Z][A-Z0-9_]{3,})\b',            # tabelas (ex: NOTA_FISCAL, DUPREC)
    r'\b([\w]+\.(?:pas|dfm|dpr))\b',         # arquivos Delphi
    r'\b(SEL_[A-Z0-9_]+)\b',                 # constantes de consulta
    r'\b(u[A-Z][A-Za-z0-9]+)\b',             # units Delphi (uGeraNotaCredDeb)
]

_STOPWORDS: set[str] = {
    "FROM", "WHERE", "JOIN", "LEFT", "INNER", "SELECT", "INSERT", "UPDATE",
    "DELETE", "CREATE", "DROP", "ALTER", "INDEX", "GROUP", "ORDER", "UNION",
    "NULL", "TRUE", "FALSE", "BEGIN", "END", "THEN", "ELSE", "WITH",
    "PROC", "RESULT", "EXIT", "FUNCTION", "PROCEDURE", "INTERFACE",
    "USES", "TYPE", "CONST", "IMPLEMENTATION", "UNIT", "PROGRAM",
    "ALTA", "MEDIA", "BAIXA", "ATIVO", "INATIVO", "NOTA", "FISCAL",
}


# ── Utilitarios ───────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Remove acentos e converte para minusculas — comparacao tolerante."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def _all_md_files(folder: Path | None = None) -> list[Path]:
    """Retorna todos os .md do vault (ou de uma subpasta), excluindo pastas ocultas."""
    root = folder or VAULT
    if not root.exists():
        return []
    return [
        p for p in root.rglob("*.md")
        if not any(part.startswith(".") for part in p.parts)
        and not any(part.startswith("_") for part in p.parts)
    ]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""


def _extract_frontmatter_field(content: str, field: str) -> str:
    """Extrai um campo do frontmatter YAML."""
    m = re.search(rf'^{field}:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_section(content: str, header: str) -> str:
    """
    Extrai o conteudo de uma secao H2 ate o proximo H2 ou fim do arquivo.
    Comparacao tolerante a acentuacao e caixa.
    """
    header_norm = _normalize(header.strip())
    lines = content.split("\n")
    inside = False
    result: list[str] = []
    for line in lines:
        if _normalize(line.strip()) == header_norm:
            inside = True
            continue
        if inside:
            if line.startswith("## "):
                break
            result.append(line)
    return "\n".join(result).strip()


def _extract_artifacts(text: str) -> set[str]:
    """Extrai artefatos tecnicos (tabelas, units, consultas) de um texto."""
    found: set[str] = set()
    for pattern in _ARTIFACT_PATTERNS:
        for m in re.findall(pattern, text):
            found.add(m.upper() if not "." in m else m.lower())
    return {
        a for a in found
        if a not in _STOPWORDS
        and len(a) >= 4
        and not re.match(r'^\d', a)
        and not re.match(r'^[A-Z]\d+$', a)
    }


# ── Comandos ──────────────────────────────────────────────────────────────────

def list_docs() -> None:
    """Lista todos os documentos do vault por tipo."""
    if not VAULT.exists():
        print(f"[VAULT NAO ENCONTRADO] {VAULT}")
        return

    print(f"=== Vault: {VAULT} ===\n")
    for tipo, folder_name in VAULT_FOLDERS.items():
        folder = VAULT / folder_name
        if not folder.exists():
            continue
        docs = list(folder.rglob("*.md"))
        if not docs:
            continue
        print(f"  {folder_name}/ ({len(docs)} docs)")
        for d in sorted(docs)[:10]:
            print(f"    - {d.stem}")
        if len(docs) > 10:
            print(f"    ... e mais {len(docs) - 10}")
        print()


def search_by_id(doc_id: str) -> None:
    """
    Busca um documento pelo ID exato (ex: RN-004, PROC-001, AG-31945).
    Mais preciso que busca por texto — usa o prefixo para limitar a pasta.
    """
    prefix = re.match(r'^([A-Z]+)', doc_id.upper())
    if not prefix:
        print(f"[ERRO] ID invalido: {doc_id}")
        return

    folder_hint = ID_PREFIXES.get(prefix.group(1))
    search_root = (VAULT / folder_hint) if folder_hint else VAULT

    matches = [
        p for p in _all_md_files(search_root)
        if doc_id.upper() in p.stem.upper()
    ]

    if not matches:
        print(f"[NAO ENCONTRADO] {doc_id} em {search_root}")
        print("\nDocumentos disponiveis nessa pasta:")
        for p in sorted(_all_md_files(search_root))[:15]:
            print(f"  - {p.stem}")
        return

    for path in matches:
        content = _read(path)
        titulo  = _extract_frontmatter_field(content, "titulo") or path.stem
        tipo    = _extract_frontmatter_field(content, "tipo")
        modulo  = _extract_frontmatter_field(content, "modulo")

        print(f"=== {path.stem} ===")
        print(f"Titulo: {titulo}")
        print(f"Tipo:   {tipo} | Modulo: {modulo}")
        print(f"Caminho: {path.relative_to(VAULT)}")
        print()

        # Exibe todas as secoes com conteudo
        for sec_key, sec_header in SECTIONS.items():
            text = _extract_section(content, sec_header)
            if text:
                print(f"--- {sec_header.replace('## ', '')} ---")
                # Limita a 40 linhas por secao para nao poluir o output
                lines = text.split("\n")
                print("\n".join(lines[:40]))
                if len(lines) > 40:
                    print(f"  ... (+{len(lines) - 40} linhas)")
                print()


def search_text(term: str, section_filter: str | None = None) -> None:
    """
    Busca um termo livre em todos os documentos do vault.
    Tolerante a acentuacao. Opcionalmente filtra por secao.
    """
    if not VAULT.exists():
        print(f"[VAULT NAO ENCONTRADO] {VAULT}")
        return

    term_norm = _normalize(term)
    matches: list[dict] = []

    for path in _all_md_files():
        content = _read(path)
        if term_norm not in _normalize(content):
            continue

        result: dict = {
            "path":     path,
            "stem":     path.stem,
            "titulo":   _extract_frontmatter_field(content, "titulo") or path.stem,
            "tipo":     _extract_frontmatter_field(content, "tipo"),
            "modulo":   _extract_frontmatter_field(content, "modulo"),
            "sections": {},
        }

        if section_filter:
            header = SECTIONS.get(section_filter)
            if header:
                text = _extract_section(content, header)
                if text and term_norm in _normalize(text):
                    result["sections"][section_filter] = text
        else:
            for key, header in SECTIONS.items():
                text = _extract_section(content, header)
                if text and term_norm in _normalize(text):
                    result["sections"][key] = text

        if result["sections"]:
            matches.append(result)

    if not matches:
        print(f'[SEM RESULTADO] Nenhum documento contem "{term}"')
        if section_filter:
            print(f'(filtro de secao: {section_filter})')
        print("\nDica: tente sem --section ou com um termo mais amplo.")
        return

    print(f'=== Resultados para "{term}" ({len(matches)} documento(s)) ===\n')
    for m in matches:
        print(f"### {m['stem']} — {m['titulo']}")
        print(f"    tipo: {m['tipo']} | modulo: {m['modulo']}")
        print(f"    path: {m['path'].relative_to(VAULT)}")
        print()
        for sec_key, sec_content in m["sections"].items():
            label = SECTIONS.get(sec_key, sec_key).replace("## ", "")
            print(f"  [{label}]")
            lines = sec_content.split("\n")
            print("\n".join(f"  {l}" for l in lines[:25]))
            if len(lines) > 25:
                print(f"  ... (+{len(lines) - 25} linhas)")
            print()


def impact_analysis(ag_key: str) -> None:
    """
    Analisa quais documentos do vault (RNs, processos) compartilham
    artefatos tecnicos com a AG informada.

    Util para identificar regressao potencial antes de implementar.
    """
    print(f"=== Analise de Impacto — {ag_key} ===\n")

    # Localiza o arquivo da AG
    ag_files = [
        p for p in _all_md_files(VAULT / "99_AGs")
        if ag_key.upper() in p.stem.upper()
    ]

    if not ag_files:
        print(f"[ERRO] AG nao encontrada: {ag_key}")
        print("Dica: verifique se a AG esta em backlog/, doing/ ou done/")
        return

    ag_path    = ag_files[0]
    ag_content = _read(ag_path)

    # Extrai artefatos da AG (de todas as secoes tecnicas)
    ag_artifacts = _extract_artifacts(ag_content)

    # Extrai tambem os IDs de RN e PROC mencionados
    rn_refs   = re.findall(r'\bRN-\d+\b', ag_content)
    proc_refs = re.findall(r'\bPROC-\d+\b', ag_content)

    print(f"AG: {ag_path.stem}")
    print(f"RNs referenciadas:      {', '.join(sorted(set(rn_refs))) or 'nenhuma'}")
    print(f"Processos referenciados:{', '.join(sorted(set(proc_refs))) or 'nenhum'}")
    if ag_artifacts:
        print(f"Artefatos detectados:   {', '.join(sorted(ag_artifacts))}")
    print()

    # Varre documentos de referencia (RNs, processos, padroes)
    ref_folders = [
        VAULT / "02_Processos",
        VAULT / "03_Regras_Negocio",
        VAULT / "04_Padroes_Tecnicos",
    ]

    impacts: list[dict] = []

    for folder in ref_folders:
        for path in _all_md_files(folder):
            if path == ag_path:
                continue

            content      = _read(path)
            doc_artifacts = _extract_artifacts(content)
            overlap      = ag_artifacts & doc_artifacts

            # Verifica se o doc e referenciado diretamente na AG
            stem_upper   = path.stem.upper()
            direct_ref   = any(ref in stem_upper for ref in rn_refs + proc_refs)

            if overlap or direct_ref:
                titulo = _extract_frontmatter_field(content, "titulo") or path.stem
                score  = len(overlap) * 2 + (5 if direct_ref else 0)
                impacts.append({
                    "path":       path,
                    "stem":       path.stem,
                    "titulo":     titulo,
                    "tipo":       _extract_frontmatter_field(content, "tipo"),
                    "overlap":    sorted(overlap),
                    "direct_ref": direct_ref,
                    "score":      score,
                })

    if not impacts:
        print("Nenhum documento de referencia compartilha artefatos com esta AG.")
        return

    impacts.sort(key=lambda x: x["score"], reverse=True)

    print(f"=== Documentos com sobreposicao ({len(impacts)} encontrado(s)) ===\n")
    for imp in impacts:
        tipo = "REFERENCIA DIRETA" if imp["direct_ref"] else "SOBREPOSICAO DE ARTEFATOS"
        print(f"[{tipo}] {imp['stem']}")
        print(f"  Titulo:  {imp['titulo']}")
        print(f"  Tipo:    {imp['tipo']}")
        if imp["overlap"]:
            print(f"  Artefatos compartilhados: {', '.join(imp['overlap'])}")
        print(f"  Path: {imp['path'].relative_to(VAULT)}")
        print()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or "--help" in args:
        print(__doc__)
        sys.exit(0)

    if "--list" in args:
        list_docs()
        sys.exit(0)

    if "--id" in args:
        idx = args.index("--id")
        if idx + 1 < len(args):
            search_by_id(args[idx + 1])
        else:
            print("[ERRO] Informe o ID: --id RN-004")
        sys.exit(0)

    if "--impact" in args:
        idx = args.index("--impact")
        if idx + 1 < len(args):
            impact_analysis(args[idx + 1])
        else:
            print("[ERRO] Informe a AG: --impact AG-XXXXX")
        sys.exit(0)

    section = None
    if "--section" in args:
        idx = args.index("--section")
        if idx + 1 < len(args):
            section = args[idx + 1]
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    term = " ".join(args)
    search_text(term, section)