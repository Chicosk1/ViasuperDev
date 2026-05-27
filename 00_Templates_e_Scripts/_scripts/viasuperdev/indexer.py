"""
indexer.py — Indexação semântica do vault e dos fontes Delphi no ChromaDB.

Camada KB (Markdown): lê todos os documentos do vault, respeita o contrato
`contexto_llm`, faz split semântico por seções (H2/H3), enriquece cada chunk
com o frontmatter como metadado e persiste na coleção 'knowledge_base'.

Camada source (Delphi): lê arquivos .pas do repositório configurado em
SOURCE_ROOT, extrai métodos como unidades semânticas e persiste na coleção
'source'. Métodos triviais (event handlers vazios, wrappers de 1 linha) são
descartados automaticamente.

Indexação incremental: mantém um manifesto JSON por camada com hash MD5 de
cada arquivo. Só reprocessa o que mudou. Use `--full` para forçar
re-indexação completa.

Uso:
    python -m viasuperdev.indexer                        # indexa só KB
    python -m viasuperdev.indexer --only kb              # indexa só KB
    python -m viasuperdev.indexer --only source          # indexa só Delphi
    python -m viasuperdev.indexer --only all             # indexa KB + source
    python -m viasuperdev.indexer --full                 # força reindexação
    python -m viasuperdev.indexer --query "base IBS"     # busca na KB
    python -m viasuperdev.indexer --query "base IBS" --collection source
    python -m viasuperdev.indexer --stats                # estatísticas
    python -m viasuperdev.indexer --dry-run              # simula sem gravar

Embedding: HuggingFaceEmbedder (local, gratuito).
  Modelo padrão: intfloat/multilingual-e5-small (384d, PT-BR nativo)
  Configurável via .env: EMBEDDINGS_PROVIDER=huggingface
                         EMBEDDINGS_MODEL=intfloat/multilingual-e5-small
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Protocol

import frontmatter

from viasuperdev import config
from viasuperdev.logging_config import setup_logging

log = logging.getLogger(__name__)

# ── Padrões Markdown ──────────────────────────────────────────────────────────
_RE_H2           = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_RE_H3           = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_RE_WIKILINK     = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]")
_RE_OBSIDIAN_TAG = re.compile(r"(?<!\w)#([a-zA-Z][\w/-]*)")

# ── Padrões Delphi ────────────────────────────────────────────────────────────
# Captura: tipo (procedure/function/constructor/destructor), modificador class,
# classe dona do método, nome, args e retorno.
# Suporta: procedure X, function X, class function X, class procedure X
_RE_DELPHI_METHOD = re.compile(
    r"^(?:class\s+)?(?P<tipo>procedure|function|constructor|destructor)"
    r"\s+(?:(?P<classe>[A-Za-z_]\w*)\.)?(?P<nome>[A-Za-z_]\w*)"
    r"(?P<args>\([^)]*\))?"
    r"(?:\s*:\s*(?P<retorno>[A-Za-z_][\w.]*))?",
    re.IGNORECASE | re.MULTILINE,
)
# Bloco entre begin..end (não aninhado — suficiente para métodos de formulário)
_RE_DELPHI_BLOCK  = re.compile(r"\bbegin\b(.+?)\bend\b", re.DOTALL | re.IGNORECASE)
# Cabeçalho de comentário estilo {--- ... ---} ou {--------...--------}
# Aceita 3+ hífens para cobrir variações de estilo nos fontes legados
_RE_DELPHI_HEADER = re.compile(r"\{-{3,}.*?-{3,}\}", re.DOTALL)
# Prefixos de unit que indicam tipo de artefato.
# "u" (genérico) é tratado como fallback no _infer_tipo — não entra aqui
# para evitar que engula prefixos mais específicos como "uf", "uc", "udm".
_DELPHI_UNIT_PREFIXES: dict[str, str] = {
    "udm":  "datamodule",
    "dm":   "datamodule",
    "ufc":  "form",
    "uf":   "form",
    "tf":   "form",
    "uc":   "form",
}
# Pastas e extensões que não têm valor semântico para RAG
_SOURCE_EXCLUDE_DIRS: set[str] = {
    "__history", "backup", "bak", ".git", "node_modules",
    "__pycache__", "bin", "obj", "debug", "release",
}
_SOURCE_EXCLUDE_SUFFIXES: set[str] = {".dfm", ".dcu", ".exe", ".dll", ".bpl"}

# Tamanho mínimo do corpo de um método para ser indexado (exclui triviais)
_DELPHI_MIN_BODY_CHARS = 60


# ── Modelos ───────────────────────────────────────────────────────────────────

@dataclass
class ChunkMetadata:
    """Metadados associados a um chunk no ChromaDB."""

    # Identificação
    doc_id:   str  # ex: PROC-001 (KB) ou uGeraNotaCredDeb.ValidarFiltros (source)
    tipo:     str  # ag/processo/regra-negocio/… (KB) | form/datamodule/unit (source)
    titulo:   str
    secao:    str  # H2 (KB) | nome do método (source)
    subsecao: str  # H3 (KB) | vazio (source)

    # Localização
    path_rel: str  # relativo a VAULT_ROOT (KB) ou SOURCE_ROOT (source)
    modulo:   str  # extraído do frontmatter (KB) | subpasta de SOURCE_ROOT (source)

    # Hash e versão
    file_hash:       str
    versao_template: str = ""

    # Metadados livres
    extras: dict = field(default_factory=dict)

    def to_flat_dict(self) -> dict:
        """ChromaDB aceita apenas tipos escalares — achata os extras."""
        flat = {
            "doc_id":          self.doc_id,
            "tipo":            self.tipo,
            "titulo":          self.titulo,
            "secao":           self.secao,
            "subsecao":        self.subsecao,
            "path_rel":        self.path_rel,
            "modulo":          self.modulo,
            "file_hash":       self.file_hash,
            "versao_template": self.versao_template,
        }
        for k, v in self.extras.items():
            if isinstance(v, list):
                flat[k] = ", ".join(str(x) for x in v)
            elif isinstance(v, (str, int, float, bool)):
                flat[k] = v
            else:
                flat[k] = str(v)
        return flat


@dataclass
class Chunk:
    """Unidade semântica indexável."""

    id:       str  # determinístico: md5(path_rel + secao + subsecao + ordem)
    text:     str
    metadata: ChunkMetadata


@dataclass
class IndexStats:
    """Estatísticas da execução de indexação."""

    arquivos_vistos:      int = 0
    arquivos_ignorados:   int = 0
    arquivos_novos:       int = 0
    arquivos_modificados: int = 0
    arquivos_inalterados: int = 0
    chunks_criados:       int = 0
    chunks_removidos:     int = 0
    erros:                list[str] = field(default_factory=list)


# ── Filtros KB ────────────────────────────────────────────────────────────────

def should_index_path(path: Path) -> bool:
    """
    Decide se um arquivo Markdown deve ser indexado com base no caminho.
    Exclui _scripts/, _templates/, _meta/ e arquivos ocultos.
    """
    parts = {p.lower() for p in path.parts}
    for excluded in config.INDEX_EXCLUDE_DIRS:
        if excluded.lower() in parts:
            return False
    if path.name.startswith("."):
        return False
    return path.suffix.lower() == ".md"


def should_index_frontmatter(fm: dict) -> bool:
    """
    Decide se um documento deve ser indexado com base no frontmatter.
    Respeita o contrato contexto_llm (alto/medio/baixo).
    """
    contexto = str(fm.get("contexto_llm", "")).lower().strip()
    if contexto in config.INDEX_EXCLUDE_CONTEXTO_LLM:
        return False
    return True


# ── Filtros source ────────────────────────────────────────────────────────────

def should_index_source_path(path: Path) -> bool:
    """
    Decide se um arquivo .pas deve ser indexado.
    Exclui pastas de histórico/backup e arquivos não-Pascal.
    """
    parts = {p.lower() for p in path.parts}
    for excluded in _SOURCE_EXCLUDE_DIRS:
        if excluded.lower() in parts:
            return False
    if path.name.startswith("."):
        return False
    return path.suffix.lower() == ".pas"


# ── Chunker de Markdown ───────────────────────────────────────────────────────

class MarkdownChunker:
    """
    Faz split de um documento Markdown em chunks semânticos por H2/H3.

    Estratégia:
      1. Lê o frontmatter (via python-frontmatter).
      2. Decide se o doc é indexável (contrato contexto_llm).
      3. Divide o corpo por H2; se um H2 tiver H3 internos, sub-divide.
      4. Normaliza wikilinks `[[foo|bar]]` → `bar`, `[[foo]]` → `foo`.
      5. Anexa o frontmatter como metadado em cada chunk.
    """

    MIN_CHUNK_CHARS = 80

    def chunk_file(self, path: Path, vault_root: Path) -> tuple[list[Chunk], bool]:
        """
        Processa um arquivo. Retorna (chunks, indexavel).
        Se indexavel=False, o chamador deve apenas registrar a estatística
        e não gravar nada no Chroma.
        """
        try:
            post = frontmatter.load(path)
        except Exception as exc:
            log.error("Falha ao parsear frontmatter de %s: %s", path, exc)
            return [], False

        fm = dict(post.metadata)
        if not should_index_frontmatter(fm):
            return [], False

        path_rel  = path.relative_to(vault_root).as_posix()
        file_hash = hash_file(path)
        body      = self._normalize_body(post.content)
        base_meta = self._build_base_metadata(path, path_rel, fm, file_hash)
        sections  = list(self._split_by_h2(body))

        if not sections:
            text = body.strip()
            if len(text) < self.MIN_CHUNK_CHARS:
                return [], True
            chunks = [self._make_chunk(text, base_meta, secao="(documento)", subsecao="", ordem=0)]
            return chunks, True

        chunks: list[Chunk] = []
        ordem = 0
        for secao_titulo, secao_corpo in sections:
            sub_chunks = list(self._split_by_h3(secao_corpo))
            if not sub_chunks:
                text = secao_corpo.strip()
                if len(text) < self.MIN_CHUNK_CHARS:
                    continue
                chunks.append(self._make_chunk(text, base_meta, secao_titulo, "", ordem))
                ordem += 1
            else:
                produced = 0
                for sub_titulo, sub_corpo in sub_chunks:
                    text = sub_corpo.strip()
                    if len(text) < self.MIN_CHUNK_CHARS:
                        continue
                    chunks.append(self._make_chunk(text, base_meta, secao_titulo, sub_titulo, ordem))
                    ordem += 1
                    produced += 1
                if produced == 0 and secao_corpo.strip():
                    chunks.append(self._make_chunk(
                        secao_corpo.strip(), base_meta, secao_titulo, "", ordem,
                    ))
                    ordem += 1
        return chunks, True

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _build_base_metadata(
        self,
        path:      Path,
        path_rel:  str,
        fm:        dict,
        file_hash: str,
    ) -> ChunkMetadata:
        doc_id = self._resolve_doc_id(path, fm)
        tipo   = str(fm.get("tipo", "")).strip().lower() or self._infer_tipo(path_rel)

        extras: dict = {}
        for key in ("tags", "status", "criticidade", "linguagem", "stack", "sistema",
                    "responsavel", "solicitante", "versao_sistema", "prioridade",
                    "data_criacao", "data_revisao"):
            if key in fm and fm[key] not in (None, "", []):
                extras[key] = fm[key]

        return ChunkMetadata(
            doc_id=doc_id,
            tipo=tipo,
            titulo=str(fm.get("titulo", path.stem)),
            secao="",
            subsecao="",
            path_rel=path_rel,
            modulo=str(fm.get("modulo", "")),
            file_hash=file_hash,
            versao_template=str(fm.get("versao_template", "")),
            extras=extras,
        )

    @staticmethod
    def _resolve_doc_id(path: Path, fm: dict) -> str:
        if "id" in fm and fm["id"]:
            return str(fm["id"]).strip()
        m = re.match(r"^([A-Z]{2,5}-[\w-]+?)(?:-|$)", path.stem)
        return m.group(1) if m else path.stem

    @staticmethod
    def _infer_tipo(path_rel: str) -> str:
        first = path_rel.split("/", 1)[0]
        return {
            "01_Indices":          "indice",
            "02_Processos":        "processo",
            "03_Regras_Negocio":   "regra-negocio",
            "04_Padroes_Tecnicos": "padrao-tecnico",
            "05_Arquiteturas":     "arquitetura",
            "06_Glossarios":       "glossario",
            "99_AGs":              "ag",
        }.get(first, "")

    @staticmethod
    def _normalize_body(text: str) -> str:
        def _replace(m: re.Match) -> str:
            target, alias = m.group(1), m.group(2)
            return (alias or target).strip()
        return _RE_WIKILINK.sub(_replace, text)

    @staticmethod
    def _split_by_h2(body: str) -> Iterator[tuple[str, str]]:
        yield from MarkdownChunker._split_by_pattern(body, _RE_H2)

    @staticmethod
    def _split_by_h3(body: str) -> Iterator[tuple[str, str]]:
        yield from MarkdownChunker._split_by_pattern(body, _RE_H3)

    @staticmethod
    def _split_by_pattern(body: str, pattern: re.Pattern) -> Iterator[tuple[str, str]]:
        matches = list(pattern.finditer(body))
        if not matches:
            return
        for i, m in enumerate(matches):
            titulo = m.group(1).strip()
            start  = m.end()
            end    = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            yield titulo, body[start:end].strip()

    @staticmethod
    def _make_chunk(
        text:     str,
        base:     ChunkMetadata,
        secao:    str,
        subsecao: str,
        ordem:    int,
    ) -> Chunk:
        meta = ChunkMetadata(
            doc_id=base.doc_id,
            tipo=base.tipo,
            titulo=base.titulo,
            secao=secao,
            subsecao=subsecao,
            path_rel=base.path_rel,
            modulo=base.modulo,
            file_hash=base.file_hash,
            versao_template=base.versao_template,
            extras=dict(base.extras),
        )
        chunk_id = _chunk_id(base.path_rel, secao, subsecao, ordem)
        prefixo = f"[{base.tipo} | {base.modulo}] {base.titulo}"
        if secao and secao != "(documento)":
            prefixo += f" › {secao}"
        if subsecao:
            prefixo += f" › {subsecao}"
        return Chunk(id=chunk_id, text=f"{prefixo}\n\n{text}", metadata=meta)


# ── Chunker de Delphi ─────────────────────────────────────────────────────────

class DelphiMethodChunker:
    """
    Extrai métodos de arquivos .pas como unidades semânticas indexáveis.

    Estratégia:
      1. Lê o arquivo .pas inteiro (tenta UTF-8, fallback para latin-1).
      2. Localiza a seção implementation.
      3. Para cada método encontrado via regex, extrai:
           - assinatura completa
           - comentário de cabeçalho {--- ... ---} se presente logo antes
           - corpo do método (entre begin..end)
      4. Descarta métodos triviais cujo corpo seja menor que _DELPHI_MIN_BODY_CHARS.
      5. Infere unit_name, class_name, modulo e tipo a partir do arquivo e caminho.

    Metadados extras por chunk:
      unit_name   — nome da unit (ex: uGeraNotaCredDeb)
      class_name  — classe do método (ex: TFGeraNotaCredDeb) ou vazio
      method_name — nome do método (ex: ValidarFiltros)
      method_type — procedure | function | constructor | destructor
    """

    def chunk_file(self, path: Path, source_root: Path) -> list[Chunk]:
        """
        Processa um arquivo .pas. Retorna lista de chunks (pode ser vazia).
        Nunca lança exceção — erros são logados e retornam [].
        """
        try:
            source = self._read_pas(path)
        except Exception as exc:
            log.error("Falha ao ler %s: %s", path, exc)
            return []

        # Só indexa o bloco implementation — interface tem apenas declarações
        impl = self._extract_implementation(source)
        if not impl:
            log.debug("Sem bloco implementation: %s", path)
            return []

        path_rel  = path.relative_to(source_root).as_posix()
        file_hash = hash_file(path)
        unit_name = path.stem
        modulo    = self._infer_modulo(path, source_root)
        tipo      = self._infer_tipo(unit_name)

        chunks: list[Chunk] = []
        ordem = 0

        for match in _RE_DELPHI_METHOD.finditer(impl):
            method_type  = match.group("tipo").lower()
            class_name   = match.group("classe") or ""
            method_name  = match.group("nome")
            args         = (match.group("args") or "").strip()
            retorno      = (match.group("retorno") or "").strip()

            # Extrai o corpo do método a partir da posição do match
            body = self._extract_body(impl, match.end())
            if not body or len(body.strip()) < _DELPHI_MIN_BODY_CHARS:
                log.debug("Descartado (trivial): %s.%s", unit_name, method_name)
                continue

            # Comentário de cabeçalho imediatamente antes da assinatura
            header_comment = self._extract_header_comment(impl, match.start())

            # Monta o texto do chunk
            assinatura = f"{method_type} {class_name + '.' if class_name else ''}{method_name}{args}"
            if retorno:
                assinatura += f": {retorno}"

            doc_id  = f"{unit_name}.{method_name}"
            secao   = method_name
            prefixo = f"[{tipo} | {modulo}] {unit_name} › {method_name}"

            text_parts = [prefixo, "", f"// {assinatura}"]
            if header_comment:
                text_parts += ["", header_comment]
            text_parts += ["", body.strip()]
            text = "\n".join(text_parts)

            meta = ChunkMetadata(
                doc_id=doc_id,
                tipo=tipo,
                titulo=unit_name,
                secao=secao,
                subsecao="",
                path_rel=path_rel,
                modulo=modulo,
                file_hash=file_hash,
                versao_template="",
                extras={
                    "unit_name":   unit_name,
                    "class_name":  class_name,
                    "method_name": method_name,
                    "method_type": method_type,
                },
            )
            chunk_id = _chunk_id(path_rel, secao, "", ordem)
            chunks.append(Chunk(id=chunk_id, text=text, metadata=meta))
            ordem += 1

        log.debug("%s → %d chunk(s) Delphi", path_rel, len(chunks))
        return chunks

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _read_pas(path: Path) -> str:
        """Lê o arquivo tentando UTF-8 e fazendo fallback para latin-1."""
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")

    @staticmethod
    def _extract_implementation(source: str) -> str:
        """Retorna o texto a partir da palavra-chave 'implementation'."""
        m = re.search(r"\bimplementation\b", source, re.IGNORECASE)
        if not m:
            return ""
        return source[m.end():]

    @staticmethod
    def _extract_body(source: str, start: int) -> str:
        """
        Extrai o corpo do método (entre begin..end) a partir de `start`.
        Lida com begin..end aninhados contando níveis.
        Retorna string vazia se não encontrar.
        """
        text    = source[start:]
        depth   = 0
        i       = 0
        begun   = False
        body_start = 0

        # Tokeniza palavras reservadas begin/end ignorando strings e comentários
        token_re = re.compile(
            r"'[^']*'"           # string literal
            r"|//[^\n]*"         # comentário de linha
            r"|\{[^}]*\}"        # comentário de bloco { }
            r"|\(\*.*?\*\)"      # comentário de bloco (* *)
            r"|\b(begin|end)\b", # tokens relevantes
            re.IGNORECASE | re.DOTALL,
        )
        for m in token_re.finditer(text):
            if not m.group(1):  # não é begin/end — é string ou comentário
                continue
            keyword = m.group(1).lower()
            if keyword == "begin":
                if not begun:
                    begun      = True
                    body_start = m.end()
                depth += 1
            elif keyword == "end" and begun:
                depth -= 1
                if depth == 0:
                    return text[body_start:m.start()].strip()
        return ""

    @staticmethod
    def _extract_header_comment(source: str, method_start: int) -> str:
        """
        Extrai o comentário de cabeçalho {--- ... ---} imediatamente antes
        da assinatura do método. Retorna string vazia se não houver.
        """
        before = source[:method_start]
        matches = list(_RE_DELPHI_HEADER.finditer(before))
        if not matches:
            return ""
        last = matches[-1]
        # Só considera o comentário se está próximo (menos de 5 linhas antes)
        gap = before[last.end():].strip()
        if gap.count("\n") > 4:
            return ""
        return last.group(0).strip()

    @staticmethod
    def _infer_modulo(path: Path, source_root: Path) -> str:
        """
        Infere o módulo a partir da subpasta imediatamente abaixo de SOURCE_ROOT.
        Ex: SOURCE_ROOT/App/Mercado/uFile.pas → 'Mercado'
            SOURCE_ROOT/uFile.pas             → '(raiz)'
        """
        try:
            parts = path.relative_to(source_root).parts
            # parts[0] pode ser 'App' — pula se for genérico demais
            if len(parts) >= 3:
                return parts[1]   # SOURCE_ROOT / App / <Modulo> / arquivo
            if len(parts) == 2:
                return parts[0]   # SOURCE_ROOT / <Modulo> / arquivo
        except ValueError:
            pass
        return "(raiz)"

    @staticmethod
    def _infer_tipo(unit_name: str) -> str:
        """
        Infere o tipo de artefato pelo prefixo do nome da unit.

        Verifica do prefixo mais longo para o mais curto para evitar que
        prefixos genericos (ex: u) engulam especificos (ex: uf, udm).
        O prefixo u (unit generica) e tratado como fallback explicito.
        """
        lower = unit_name.lower()
        for prefix, tipo in sorted(_DELPHI_UNIT_PREFIXES.items(), key=lambda x: -len(x[0])):
            if lower.startswith(prefix):
                return tipo
        if lower.startswith("u"):
            return "unit"
        return "unit"


# ── Helpers comuns ────────────────────────────────────────────────────────────

def _chunk_id(path_rel: str, secao: str, subsecao: str, ordem: int) -> str:
    raw = f"{path_rel}::{secao}::{subsecao}::{ordem}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def hash_file(path: Path) -> str:
    """MD5 do conteúdo do arquivo — usado para indexação incremental."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


# ── Embedder (interface + implementações) ─────────────────────────────────────

class Embedder(Protocol):
    """Contrato mínimo para qualquer backend de embedding."""

    name:       str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


class HuggingFaceEmbedder:
    """
    Backend de embedding local via sentence-transformers (sem custo de API).

    Modelo padrão: intfloat/multilingual-e5-small
      - Dimensões:   384
      - Suporte:     PT-BR nativo (multilingual)
      - Tamanho:     ~120 MB (download único no primeiro uso)
      - Licença:     MIT — uso comercial permitido

    Modelos alternativos (troque via EMBEDDINGS_MODEL no .env):
      intfloat/multilingual-e5-base  → 768d, melhor qualidade, ~280 MB
      BAAI/bge-small-en-v1.5         → 384d, apenas inglês, muito rápido
    """

    name = "huggingface"

    def __init__(self, model: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Pacote 'sentence-transformers' não instalado. "
                "Adicione em pyproject.toml e regenere requirements.txt com pip-compile."
            ) from exc

        log.info("Carregando modelo de embedding local: %s", model)
        self._model     = SentenceTransformer(model)
        self.model      = model
        self.dimensions = self._model.get_sentence_embedding_dimension()
        log.info("Modelo carregado — dimensões: %d", self.dimensions)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vector.tolist()


class VoyageEmbedder:
    """
    Backend Voyage AI (legado — mantido para compatibilidade).
    Para usar: EMBEDDINGS_PROVIDER=voyage + VOYAGE_API_KEY no .env.
    """

    name = "voyage"

    def __init__(self, model: str, api_key: str) -> None:
        try:
            import voyageai  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Pacote 'voyageai' não instalado. Adicione em pyproject.toml e "
                "regenere requirements.txt com pip-compile."
            ) from exc
        self._client    = voyageai.Client(api_key=api_key)
        self.model      = model
        self.dimensions = 1024

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        batches: list[list[float]] = []
        for i in range(0, len(texts), 128):
            chunk = texts[i:i + 128]
            resp  = self._client.embed(chunk, model=self.model, input_type="document")
            batches.extend(resp.embeddings)
        return batches

    def embed_query(self, text: str) -> list[float]:
        resp = self._client.embed([text], model=self.model, input_type="query")
        return resp.embeddings[0]


def build_embedder() -> Embedder:
    """
    Constrói o embedder configurado em config.py.

    Providers (EMBEDDINGS_PROVIDER no .env):
      huggingface  — local, gratuito (padrão)
      voyage       — API Voyage AI (requer VOYAGE_API_KEY)

    Atenção: trocar de provider requer --full em ambas as coleções.
    """
    provider = config.EMBEDDINGS_PROVIDER.lower()

    if provider == "huggingface":
        return HuggingFaceEmbedder(config.EMBEDDINGS_MODEL)

    if provider == "voyage":
        if not config.VOYAGE_API_KEY:
            log.error("VOYAGE_API_KEY ausente no .env — necessário para o provider 'voyage'.")
            sys.exit(1)
        return VoyageEmbedder(config.EMBEDDINGS_MODEL, config.VOYAGE_API_KEY)

    raise ValueError(
        f"Provider de embeddings não suportado: '{provider}'. "
        "Valores aceitos: 'huggingface', 'voyage'."
    )


# ── ChromaDB store ────────────────────────────────────────────────────────────

def get_collection(name: str, embedder: Embedder):
    """
    Retorna (ou cria) uma coleção do ChromaDB.
    embedding_function=None é intencional — vetores calculados externamente.
    """
    try:
        import chromadb  # type: ignore
        from chromadb.config import Settings  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Pacote 'chromadb' não instalado. Adicione em pyproject.toml e "
            "regenere requirements.txt com pip-compile."
        ) from exc

    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=name,
        metadata={
            "embedder":   embedder.name,
            "model":      getattr(embedder, "model", ""),
            "dimensions": embedder.dimensions,
        },
    )


# ── Manifestos (um por camada) ────────────────────────────────────────────────

def _manifest_path(camada: str = "kb") -> Path:
    """Caminho do manifesto para a camada informada (kb ou source)."""
    return config.CHROMA_DIR / f"manifest_{camada}.json"


def load_manifest(camada: str = "kb") -> dict[str, str]:
    """Carrega o manifesto path_rel → file_hash da camada. Retorna {} se não existir."""
    p = _manifest_path(camada)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.warning("Manifesto %s corrompido (%s) — reindexação completa forçada.", camada, exc)
        return {}


def save_manifest(manifest: dict[str, str], camada: str = "kb") -> None:
    p = _manifest_path(camada)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Pipeline KB ───────────────────────────────────────────────────────────────

def index_kb(*, full: bool = False, dry_run: bool = False) -> IndexStats:
    """Indexa toda a camada KB (Markdown) do vault."""
    stats      = IndexStats()
    chunker    = MarkdownChunker()
    embedder   = build_embedder() if not dry_run else None
    collection = get_collection("knowledge_base", embedder) if not dry_run else None
    manifest   = {} if full else load_manifest("kb")

    log.info("Varrendo vault: %s", config.VAULT_ROOT)
    md_files = sorted(p for p in config.VAULT_ROOT.rglob("*.md") if should_index_path(p))
    log.info("Arquivos Markdown candidatos: %d", len(md_files))

    novo_manifest: dict[str, str] = {}

    for path in md_files:
        stats.arquivos_vistos += 1
        path_rel  = path.relative_to(config.VAULT_ROOT).as_posix()
        file_hash = hash_file(path)

        if not full and manifest.get(path_rel) == file_hash:
            stats.arquivos_inalterados += 1
            novo_manifest[path_rel] = file_hash
            continue

        try:
            chunks, indexavel = chunker.chunk_file(path, config.VAULT_ROOT)
        except Exception as exc:
            msg = f"{path_rel}: {exc}"
            log.error("Erro processando %s", msg)
            stats.erros.append(msg)
            continue

        if not indexavel:
            stats.arquivos_ignorados += 1
            log.debug("Ignorado (contexto_llm=baixo): %s", path_rel)
            continue

        if not chunks:
            stats.arquivos_ignorados += 1
            log.debug("Sem chunks úteis: %s", path_rel)
            continue

        if path_rel in manifest:
            stats.arquivos_modificados += 1
            if not dry_run and collection is not None:
                _delete_chunks_of(collection, path_rel)
        else:
            stats.arquivos_novos += 1

        if dry_run:
            log.info("[DRY] %s → %d chunk(s)", path_rel, len(chunks))
        else:
            assert embedder is not None and collection is not None
            _upsert_chunks(collection, embedder, chunks)
            log.info("Indexado: %s (%d chunk(s))", path_rel, len(chunks))

        stats.chunks_criados += len(chunks)
        novo_manifest[path_rel] = file_hash

    if not full:
        removidos = set(manifest) - set(novo_manifest) - {
            p.relative_to(config.VAULT_ROOT).as_posix()
            for p in md_files if not should_index_path(p)
        }
        for path_rel in removidos:
            if dry_run:
                log.info("[DRY] removeria do índice KB: %s", path_rel)
            elif collection is not None:
                deleted = _delete_chunks_of(collection, path_rel)
                stats.chunks_removidos += deleted
                log.info("Removido do índice KB: %s (%d chunk(s))", path_rel, deleted)

    if not dry_run:
        save_manifest(novo_manifest, "kb")
    return stats


# ── Pipeline source ───────────────────────────────────────────────────────────

def index_source(*, full: bool = False, dry_run: bool = False) -> IndexStats:
    """Indexa toda a camada source (Delphi .pas) do repositório configurado."""
    if not config.SOURCE_ROOT or not config.SOURCE_ROOT.exists():
        log.error(
            "SOURCE_ROOT não configurado ou não encontrado: '%s'. "
            "Defina SOURCE_ROOT no .env apontando para a raiz do repositório Delphi.",
            config.SOURCE_ROOT,
        )
        return IndexStats(erros=["SOURCE_ROOT inválido — verifique o .env"])

    stats      = IndexStats()
    chunker    = DelphiMethodChunker()
    embedder   = build_embedder() if not dry_run else None
    collection = get_collection("source", embedder) if not dry_run else None
    manifest   = {} if full else load_manifest("source")

    log.info("Varrendo source: %s", config.SOURCE_ROOT)
    pas_files = sorted(
        p for p in config.SOURCE_ROOT.rglob("*.pas")
        if should_index_source_path(p)
    )
    log.info("Arquivos .pas candidatos: %d", len(pas_files))

    novo_manifest: dict[str, str] = {}

    for path in pas_files:
        stats.arquivos_vistos += 1
        path_rel  = path.relative_to(config.SOURCE_ROOT).as_posix()
        file_hash = hash_file(path)

        if not full and manifest.get(path_rel) == file_hash:
            stats.arquivos_inalterados += 1
            novo_manifest[path_rel] = file_hash
            continue

        try:
            chunks = chunker.chunk_file(path, config.SOURCE_ROOT)
        except Exception as exc:
            msg = f"{path_rel}: {exc}"
            log.error("Erro processando %s", msg)
            stats.erros.append(msg)
            continue

        if not chunks:
            stats.arquivos_ignorados += 1
            log.debug("Sem chunks úteis (unit sem métodos indexáveis): %s", path_rel)
            continue

        if path_rel in manifest:
            stats.arquivos_modificados += 1
            if not dry_run and collection is not None:
                _delete_chunks_of(collection, path_rel)
        else:
            stats.arquivos_novos += 1

        if dry_run:
            log.info("[DRY] %s → %d chunk(s)", path_rel, len(chunks))
        else:
            assert embedder is not None and collection is not None
            _upsert_chunks(collection, embedder, chunks)
            log.info("Indexado: %s (%d chunk(s))", path_rel, len(chunks))

        stats.chunks_criados += len(chunks)
        novo_manifest[path_rel] = file_hash

    if not full:
        removidos = set(manifest) - set(novo_manifest) - {
            p.relative_to(config.SOURCE_ROOT).as_posix()
            for p in pas_files if not should_index_source_path(p)
        }
        for path_rel in removidos:
            if dry_run:
                log.info("[DRY] removeria do índice source: %s", path_rel)
            elif collection is not None:
                deleted = _delete_chunks_of(collection, path_rel)
                stats.chunks_removidos += deleted
                log.info("Removido do índice source: %s (%d chunk(s))", path_rel, deleted)

    if not dry_run:
        save_manifest(novo_manifest, "source")
    return stats


# ── Helpers de pipeline ───────────────────────────────────────────────────────

def _upsert_chunks(collection, embedder: Embedder, chunks: list[Chunk]) -> None:
    texts      = [c.text for c in chunks]
    embeddings = embedder.embed_documents(texts)
    collection.upsert(
        ids=[c.id for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[c.metadata.to_flat_dict() for c in chunks],
    )


def _delete_chunks_of(collection, path_rel: str) -> int:
    existing = collection.get(where={"path_rel": path_rel}, include=[])
    ids = existing.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)


# ── Query e estatísticas ──────────────────────────────────────────────────────

_COLLECTION_MAP = {
    "kb":     "knowledge_base",
    "source": "source",
}


def query_collection(text: str, collection_name: str = "kb", k: int = 5) -> list[dict]:
    """Consulta uma coleção e retorna os top-k resultados."""
    chroma_name = _COLLECTION_MAP.get(collection_name, collection_name)
    embedder    = build_embedder()
    collection  = get_collection(chroma_name, embedder)
    vector      = embedder.embed_query(text)
    res         = collection.query(query_embeddings=[vector], n_results=k)

    out: list[dict] = []
    ids       = (res.get("ids") or [[]])[0]
    docs      = (res.get("documents") or [[]])[0]
    metas     = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]
    for i, _id in enumerate(ids):
        out.append({
            "id":       _id,
            "score":    1 - distances[i] if i < len(distances) else None,
            "metadata": metas[i] if i < len(metas) else {},
            "preview":  (docs[i][:240] + "…") if i < len(docs) and len(docs[i]) > 240 else docs[i],
        })
    return out


# Alias retrocompatível com código existente que chama query_kb diretamente
def query_kb(text: str, k: int = 5) -> list[dict]:
    return query_collection(text, "kb", k)


def show_stats() -> None:
    """Imprime estatísticas de todas as coleções indexadas."""
    embedder = build_embedder()

    for label, chroma_name in _COLLECTION_MAP.items():
        try:
            collection = get_collection(chroma_name, embedder)
            total      = collection.count()
            manifest   = load_manifest(label)
        except Exception:
            continue

        print(f"\n{'=' * 60}")
        print(f"  Coleção: {label} ({chroma_name})")
        print(f"  Diretório: {config.CHROMA_DIR}")
        print(f"  Total de chunks: {total}")
        print(f"  Embedder: {embedder.name} ({getattr(embedder, 'model', '?')}, {embedder.dimensions}d)")
        print(f"  Arquivos no manifesto: {len(manifest)}")
        if manifest:
            print("  Últimos 5 arquivos indexados:")
            for path_rel in sorted(manifest)[-5:]:
                print(f"    • {path_rel}")
    print(f"\n{'=' * 60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="viasuperdev.indexer",
        description="Indexação semântica do vault e dos fontes Delphi no ChromaDB.",
    )
    p.add_argument(
        "--only",
        choices=["kb", "source", "all"],
        default="kb",
        help="Camada a indexar: kb (Markdown), source (Delphi) ou all (ambas). Default: kb.",
    )
    p.add_argument(
        "--full",
        action="store_true",
        help="Ignora o manifesto e re-indexa todos os arquivos.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o que seria feito sem gravar no Chroma.",
    )
    p.add_argument(
        "--query",
        metavar="TEXTO",
        help="Não indexa — consulta a coleção com o texto fornecido.",
    )
    p.add_argument(
        "--collection",
        choices=["kb", "source"],
        default="kb",
        help="Coleção a consultar com --query (default: kb).",
    )
    p.add_argument(
        "--k",
        type=int,
        default=5,
        help="Número de resultados de --query (default: 5).",
    )
    p.add_argument(
        "--stats",
        action="store_true",
        help="Não indexa — mostra estatísticas de todas as coleções.",
    )
    return p


def _print_query_results(results: list[dict], collection: str = "kb") -> None:
    if not results:
        print("\n  Nenhum resultado encontrado.\n")
        return
    print(f"\n{'=' * 60}  [{collection}]")
    for i, r in enumerate(results, 1):
        meta      = r["metadata"]
        score     = r["score"]
        score_str = f"{score:.3f}" if score is not None else "—"
        print(f"\n  [{i}] score={score_str}")
        print(f"      {meta.get('doc_id', '?')} | {meta.get('tipo', '?')} | {meta.get('modulo', '?')}")
        secao   = meta.get("secao", "")
        subsecao = meta.get("subsecao", "")
        print(f"      § {secao} {('› ' + subsecao) if subsecao else ''}")
        print(f"      {meta.get('path_rel', '')}")
        print(f"      {r['preview']}")
    print(f"\n{'=' * 60}\n")


def _print_stats(stats: IndexStats, label: str, elapsed: float) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Indexação [{label}] concluída em {elapsed:.1f}s")
    print(f"  Vistos:         {stats.arquivos_vistos}")
    print(f"    Novos:        {stats.arquivos_novos}")
    print(f"    Modificados:  {stats.arquivos_modificados}")
    print(f"    Inalterados:  {stats.arquivos_inalterados}")
    print(f"    Ignorados:    {stats.arquivos_ignorados}")
    print(f"  Chunks criados:   {stats.chunks_criados}")
    print(f"  Chunks removidos: {stats.chunks_removidos}")
    if stats.erros:
        print(f"\n  Erros ({len(stats.erros)}):")
        for e in stats.erros:
            print(f"    • {e}")
    print(f"{'=' * 60}\n")


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    args = _build_argparser().parse_args(argv)
    config.validate()

    if args.query:
        results = query_collection(args.query, args.collection, k=args.k)
        _print_query_results(results, args.collection)
        return 0

    if args.stats:
        show_stats()
        return 0

    erros_totais = 0

    if args.only in ("kb", "all"):
        started = time.perf_counter()
        stats   = index_kb(full=args.full, dry_run=args.dry_run)
        _print_stats(stats, "KB", time.perf_counter() - started)
        erros_totais += len(stats.erros)

    if args.only in ("source", "all"):
        started = time.perf_counter()
        stats   = index_source(full=args.full, dry_run=args.dry_run)
        _print_stats(stats, "source", time.perf_counter() - started)
        erros_totais += len(stats.erros)

    return 0 if not erros_totais else 1


if __name__ == "__main__":
    sys.exit(main())