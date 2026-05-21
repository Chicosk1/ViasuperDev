"""
test_vault_writer.py — Testes unitários para vault_writer.py.

Usa tmp_path do pytest para não tocar no vault real.
Roda com: make test
"""

from __future__ import annotations

from pathlib import Path

import pytest

from viasuperdev.vault_writer import next_id, slugify


# ── Testes: slugify ───────────────────────────────────────────────────────────

class TestSlugify:
    def test_converte_para_minusculas(self):
        assert slugify("Nota Fiscal") == "nota-fiscal"

    def test_remove_acentos(self):
        assert slugify("Geração de Crédito") == "geracao-de-credito"

    def test_substitui_espacos_por_hifen(self):
        assert slugify("gerar notas em massa") == "gerar-notas-em-massa"

    def test_remove_caracteres_especiais(self):
        assert slugify("ag-xxxxx: Notas (2/2)") == "ag-xxxxx-notas-22"

    def test_trunca_em_70_chars(self):
        longo = "a" * 100
        assert len(slugify(longo)) <= 70

    def test_sem_hifen_no_inicio_ou_fim(self):
        result = slugify("  espaços nas bordas  ")
        assert not result.startswith("-")
        assert not result.endswith("-")

    def test_string_vazia(self):
        assert slugify("") == ""


# ── Testes: next_id ───────────────────────────────────────────────────────────

class TestNextId:
    def test_primeira_nota_retorna_001(self, tmp_path: Path):
        assert next_id(tmp_path, "PROC") == "PROC-001"

    def test_incrementa_apos_existentes(self, tmp_path: Path):
        (tmp_path / "PROC-001-nome.md").touch()
        (tmp_path / "PROC-002-outro.md").touch()
        assert next_id(tmp_path, "PROC") == "PROC-003"

    def test_encontra_maior_id_nao_sequencial(self, tmp_path: Path):
        (tmp_path / "PROC-001-nome.md").touch()
        (tmp_path / "PROC-005-salto.md").touch()
        assert next_id(tmp_path, "PROC") == "PROC-006"

    def test_busca_em_subpastas(self, tmp_path: Path):
        sub = tmp_path / "subpasta"
        sub.mkdir()
        (sub / "RN-003-regra.md").touch()
        assert next_id(tmp_path, "RN") == "RN-004"

    def test_ignora_arquivos_sem_prefixo(self, tmp_path: Path):
        (tmp_path / "README.md").touch()
        (tmp_path / "indice-geral.md").touch()
        assert next_id(tmp_path, "ARQ") == "ARQ-001"

    def test_prefixo_case_insensitive(self, tmp_path: Path):
        (tmp_path / "proc-002-minusculo.md").touch()
        assert next_id(tmp_path, "PROC") == "PROC-003"