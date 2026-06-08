"""
test_indexer.py — Cobre MarkdownChunker, filtros, manifesto, hash e embedders.

Não testa integrações de rede nem ChromaDB de fato:
essas são responsabilidade de testes de integração separados.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from viasuperdev import config
from viasuperdev.indexer import (
    ChunkMetadata,
    HuggingFaceEmbedder,
    MarkdownChunker,
    VoyageEmbedder,
    build_embedder,
    hash_file,
    load_manifest,
    save_manifest,
    should_index_frontmatter,
    should_index_path,
)


# ── should_index_path ─────────────────────────────────────────────────────────

class TestShouldIndexPath:
    def test_aceita_md_em_pasta_normal(self, tmp_path: Path) -> None:
        f = tmp_path / "03_Regras_Negocio" / "nota" / "RN-001.md"
        f.parent.mkdir(parents=True)
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is True

    def test_rejeita_arquivo_em_scripts(self, tmp_path: Path) -> None:
        f = tmp_path / "00_Templates_e_Scripts" / "_scripts" / "viasuperdev" / "x.md"
        f.parent.mkdir(parents=True)
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is False

    def test_rejeita_arquivo_em_templates(self, tmp_path: Path) -> None:
        f = tmp_path / "00_Templates_e_Scripts" / "_templates" / "Template_AG.md"
        f.parent.mkdir(parents=True)
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is False

    def test_rejeita_arquivo_em_meta(self, tmp_path: Path) -> None:
        f = tmp_path / "_meta" / "qualquer.md"
        f.parent.mkdir(parents=True)
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is False

    def test_rejeita_arquivo_oculto(self, tmp_path: Path) -> None:
        f = tmp_path / ".secret.md"
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is False

    def test_rejeita_nao_markdown(self, tmp_path: Path) -> None:
        f = tmp_path / "arquivo.txt"
        f.write_text("ok", encoding="utf-8")
        assert should_index_path(f) is False


# ── should_index_frontmatter ──────────────────────────────────────────────────

class TestShouldIndexFrontmatter:
    def test_aceita_contexto_alto(self) -> None:
        assert should_index_frontmatter({"contexto_llm": "alto"}) is True

    def test_aceita_contexto_medio(self) -> None:
        assert should_index_frontmatter({"contexto_llm": "medio"}) is True

    def test_rejeita_contexto_baixo(self) -> None:
        assert should_index_frontmatter({"contexto_llm": "baixo"}) is False

    def test_rejeita_contexto_baixo_case_insensitive(self) -> None:
        assert should_index_frontmatter({"contexto_llm": "BAIXO"}) is False

    def test_aceita_sem_contexto_definido(self) -> None:
        assert should_index_frontmatter({}) is True


# ── hash_file ─────────────────────────────────────────────────────────────────

class TestHashFile:
    def test_hash_estavel_para_mesmo_conteudo(self, tmp_path: Path) -> None:
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("conteudo identico", encoding="utf-8")
        b.write_text("conteudo identico", encoding="utf-8")
        assert hash_file(a) == hash_file(b)

    def test_hash_muda_quando_conteudo_muda(self, tmp_path: Path) -> None:
        f = tmp_path / "a.md"
        f.write_text("versao 1", encoding="utf-8")
        h1 = hash_file(f)
        f.write_text("versao 2", encoding="utf-8")
        assert hash_file(f) != h1


# ── Manifesto ─────────────────────────────────────────────────────────────────

class TestManifesto:
    def test_load_manifesto_vazio(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(config, "CHROMA_DIR", tmp_path)
        assert load_manifest() == {}

    def test_round_trip(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(config, "CHROMA_DIR", tmp_path)
        data = {"03_Regras/RN-001.md": "abc123", "02_Processos/PROC-001.md": "def456"}
        save_manifest(data)
        assert load_manifest() == data

    def test_load_manifesto_corrompido_retorna_vazio(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(config, "CHROMA_DIR", tmp_path)
        (tmp_path / "manifest.json").write_text("{ json invalido", encoding="utf-8")
        assert load_manifest() == {}


# ── MarkdownChunker ───────────────────────────────────────────────────────────

_DOC_PROCESSO = """\
---
id: PROC-001
tipo: processo
titulo: Gerar Notas de Crédito/Débito em Massa
modulo: nota
contexto_llm: alto
versao_template: "1.0"
tags:
  - nota
  - reforma-tributaria
sistema: viasuper
---

## 1. Objetivo

Permitir a geração em massa de notas de crédito e débito a partir de duplicatas
elegíveis no contexto da reforma tributária IBS/CBS.

## 2. Fluxo

1. Usuário acessa a tela GeraNotaCredDebito.
2. Define filtros de data obrigatórios.
3. Sistema lista duplicatas elegíveis.

### 2.1 Filtros aplicados

Os filtros de data são obrigatórios e seguem a [[RN-001-filtro-data-obrigatorio|RN-001]].
Detalhes completos no documento referenciado acima sobre filtros de data.

### 2.2 Validações

Cada duplicata passa por checagem de elegibilidade conforme RN-002. As regras
incluem verificação de status, prazo e tipo de operação fiscal.

## 3. Componentes

Unit `UGeraNotaCredDeb.pas` é o ponto de entrada principal da rotina, com as
tabelas `NOTA_FISCAL` e `DUPLICATA` sendo as fontes de dados primárias.
"""

_DOC_CONTEXTO_BAIXO = """\
---
id: IDX-nota
tipo: indice
titulo: Índice do módulo Nota
modulo: nota
contexto_llm: baixo
versao_template: "1.0"
---

## Links

- PROC-001
- RN-001
"""

_DOC_SEM_H2 = """\
---
id: GLOS-nota
tipo: glossario
titulo: Glossário do módulo Nota
modulo: nota
contexto_llm: alto
versao_template: "1.0"
---

Documento sem cabeçalhos H2 — deve gerar exatamente um chunk com o corpo todo,
desde que ultrapasse o mínimo de caracteres exigido pelo chunker para evitar
chunks vazios ou semanticamente pobres.
"""


class TestMarkdownChunker:
    def test_processo_completo_gera_chunks_por_secao(self, tmp_path: Path) -> None:
        f = tmp_path / "PROC-001-gerar.md"
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks, indexavel = MarkdownChunker().chunk_file(f, tmp_path)

        assert indexavel is True
        assert len(chunks) >= 3
        secoes = [c.metadata.secao for c in chunks]
        assert any("Objetivo" in s for s in secoes)
        subsecoes = [c.metadata.subsecao for c in chunks]
        assert any("Filtros" in s for s in subsecoes)

    def test_doc_contexto_baixo_e_ignorado(self, tmp_path: Path) -> None:
        f = tmp_path / "IDX-nota.md"
        f.write_text(_DOC_CONTEXTO_BAIXO, encoding="utf-8")

        chunks, indexavel = MarkdownChunker().chunk_file(f, tmp_path)

        assert indexavel is False
        assert chunks == []

    def test_doc_sem_h2_vira_chunk_unico(self, tmp_path: Path) -> None:
        f = tmp_path / "GLOS-nota.md"
        f.write_text(_DOC_SEM_H2, encoding="utf-8")

        chunks, indexavel = MarkdownChunker().chunk_file(f, tmp_path)

        assert indexavel is True
        assert len(chunks) == 1
        assert chunks[0].metadata.secao == "(documento)"

    def test_metadados_extraidos_do_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "PROC-001-gerar.md"
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks, _ = MarkdownChunker().chunk_file(f, tmp_path)
        meta = chunks[0].metadata

        assert meta.doc_id          == "PROC-001"
        assert meta.tipo            == "processo"
        assert meta.modulo          == "nota"
        assert meta.versao_template == "1.0"
        assert meta.titulo.startswith("Gerar Notas")

    def test_wikilinks_sao_resolvidos_no_texto(self, tmp_path: Path) -> None:
        f = tmp_path / "PROC-001-gerar.md"
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks, _ = MarkdownChunker().chunk_file(f, tmp_path)
        full_text = "\n".join(c.text for c in chunks)

        assert "[[" not in full_text
        assert "RN-001" in full_text

    def test_chunk_id_e_deterministico(self, tmp_path: Path) -> None:
        f = tmp_path / "PROC-001-gerar.md"
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks_a, _ = MarkdownChunker().chunk_file(f, tmp_path)
        chunks_b, _ = MarkdownChunker().chunk_file(f, tmp_path)

        assert [c.id for c in chunks_a] == [c.id for c in chunks_b]

    def test_path_rel_usa_forward_slash(self, tmp_path: Path) -> None:
        f = tmp_path / "02_Processos" / "nota" / "PROC-001.md"
        f.parent.mkdir(parents=True)
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks, _ = MarkdownChunker().chunk_file(f, tmp_path)

        assert "/" in chunks[0].metadata.path_rel
        assert "\\" not in chunks[0].metadata.path_rel

    def test_tags_lista_sao_preservadas_em_extras(self, tmp_path: Path) -> None:
        f = tmp_path / "PROC-001-gerar.md"
        f.write_text(_DOC_PROCESSO, encoding="utf-8")

        chunks, _ = MarkdownChunker().chunk_file(f, tmp_path)
        meta = chunks[0].metadata

        assert "tags" in meta.extras
        assert meta.extras["tags"] == ["nota", "reforma-tributaria"]

    def test_fallback_indexa_h2_quando_todas_h3_muito_curtas(self, tmp_path: Path) -> None:
        """
        Se todas as subseções H3 são curtas demais, o chunker não pode
        descartá-las silenciosamente — precisa indexar o H2 inteiro como fallback,
        senão informação importante (porém concisa) some do índice.
        """
        doc = """---
id: RN-X
tipo: regra-negocio
titulo: Caso de borda
modulo: nota
contexto_llm: alto
versao_template: "1.0"
---

## 3. Casos de Borda

### 3.1 Data vazia
Erro 1001.

### 3.2 Data invertida
Erro 1002.
"""
        f = tmp_path / "RN-X.md"
        f.write_text(doc, encoding="utf-8")

        chunks, indexavel = MarkdownChunker().chunk_file(f, tmp_path)

        assert indexavel is True
        assert len(chunks) == 1
        assert chunks[0].metadata.secao == "3. Casos de Borda"
        assert chunks[0].metadata.subsecao == ""
        assert "1001" in chunks[0].text
        assert "1002" in chunks[0].text


# ── ChunkMetadata.to_flat_dict ────────────────────────────────────────────────

class TestChunkMetadataFlat:
    def test_lista_vira_string_separada_por_virgula(self) -> None:
        meta = ChunkMetadata(
            doc_id="PROC-001",
            tipo="processo",
            titulo="t",
            secao="s",
            subsecao="",
            path_rel="p.md",
            modulo="nota",
            file_hash="abc",
            extras={"tags": ["a", "b", "c"]},
        )
        flat = meta.to_flat_dict()
        assert flat["tags"] == "a, b, c"

    def test_escalares_sao_preservados(self) -> None:
        meta = ChunkMetadata(
            doc_id="PROC-001",
            tipo="processo",
            titulo="t",
            secao="s",
            subsecao="",
            path_rel="p.md",
            modulo="nota",
            file_hash="abc",
            extras={"criticidade": "alta", "ordem": 3},
        )
        flat = meta.to_flat_dict()
        assert flat["criticidade"] == "alta"
        assert flat["ordem"] == 3


# ── HuggingFaceEmbedder ───────────────────────────────────────────────────────

class TestHuggingFaceEmbedder:
    """
    Testes unitários do HuggingFaceEmbedder com SentenceTransformer mockado.
    Não fazem download nem chamam GPU/CPU real — isolados e rápidos.
    """

    def _make_embedder(self, dims: int = 384) -> HuggingFaceEmbedder:
        """Cria um HuggingFaceEmbedder com SentenceTransformer totalmente mockado."""
        import numpy as np

        mock_st = MagicMock()
        mock_st.get_sentence_embedding_dimension.return_value = dims
        mock_st.encode.side_effect = lambda texts, **kw: (
            np.random.rand(dims).astype("float32")
            if isinstance(texts, str) 
            else np.random.rand(len(texts), dims).astype("float32")
        )

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_st):
            embedder = HuggingFaceEmbedder("intfloat/multilingual-e5-small")

        embedder._model = mock_st
        return embedder

    def test_dimensoes_inferidas_do_modelo(self) -> None:
        embedder = self._make_embedder(dims=384)
        assert embedder.dimensions == 384
        assert embedder.name == "huggingface"

    def test_embed_documents_retorna_lista_de_vetores(self) -> None:
        embedder = self._make_embedder(dims=384)
        texts = ["regra de negócio IBS", "cálculo CBS proporcional"]
        result = embedder.embed_documents(texts)

        assert len(result) == 2
        assert all(len(v) == 384 for v in result)
        assert all(isinstance(x, float) for v in result for x in v)

    def test_embed_query_retorna_vetor_unico(self) -> None:
        embedder = self._make_embedder(dims=384)
        vector = embedder.embed_query("base de cálculo IBS")

        assert len(vector) == 384
        assert all(isinstance(x, float) for x in vector)

    def test_embed_documents_lista_vazia(self) -> None:
        import numpy as np

        mock_st = MagicMock()
        mock_st.get_sentence_embedding_dimension.return_value = 384
        mock_st.encode.return_value = np.array([]).reshape(0, 384).astype("float32")

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_st):
            embedder = HuggingFaceEmbedder("intfloat/multilingual-e5-small")

        embedder._model = mock_st
        result = embedder.embed_documents([])
        assert result == []

    def test_importerror_levanta_runtime_com_mensagem_clara(self) -> None:
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            with pytest.raises(RuntimeError, match="sentence-transformers"):
                HuggingFaceEmbedder("qualquer-modelo")


# ── build_embedder ────────────────────────────────────────────────────────────

class TestBuildEmbedder:
    def test_provider_huggingface_instancia_hf_embedder(self, monkeypatch) -> None:
        monkeypatch.setattr(config, "EMBEDDINGS_PROVIDER", "huggingface")
        monkeypatch.setattr(config, "EMBEDDINGS_MODEL", "intfloat/multilingual-e5-small")

        import numpy as np
        mock_st = MagicMock()
        mock_st.get_sentence_embedding_dimension.return_value = 384
        mock_st.encode.return_value = np.zeros((1, 384), dtype="float32")

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_st):
            embedder = build_embedder()

        assert isinstance(embedder, HuggingFaceEmbedder)
        assert embedder.name == "huggingface"

    def test_provider_voyage_sem_chave_chama_sys_exit(self, monkeypatch) -> None:
        monkeypatch.setattr(config, "EMBEDDINGS_PROVIDER", "voyage")
        monkeypatch.setattr(config, "VOYAGE_API_KEY", "")

        with pytest.raises(SystemExit):
            build_embedder()

    def test_provider_invalido_levanta_valueerror(self, monkeypatch) -> None:
        monkeypatch.setattr(config, "EMBEDDINGS_PROVIDER", "openai")

        with pytest.raises(ValueError, match="openai"):
            build_embedder()