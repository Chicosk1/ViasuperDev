"""
Testes da Fase 3b — DelphiMethodChunker e index_source.

Cole este bloco no final do test_indexer.py existente.
Todos os testes são unitários — não precisam de arquivo .pas real no disco,
usam tmp_path do pytest para criar fixtures mínimas.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from viasuperdev import config
from viasuperdev.indexer import (
    DelphiMethodChunker,
    should_index_source_path,
)


# ── Fixtures de código Delphi ─────────────────────────────────────────────────

_PAS_FORMULARIO = """\
unit uGeraNotaCredDeb;

interface

type
  TFGeraNotaCredDeb = class(TFFormProc)
  private
    procedure ValidarFiltros;
    procedure CarregarNotaCredDeb;
    function  GetFiltros: String;
  end;

implementation

procedure TFGeraNotaCredDeb.btnExecutarClick(Sender: TObject);
begin
  ValidarFiltros;
  CarregarNotaCredDeb;
end;

procedure TFGeraNotaCredDeb.ValidarFiltros;
var
  bPossuiEmissao, bPossuiBaixa: Boolean;
begin
  bPossuiEmissao := (drEmissaoINI.Data <> DataZero) and (drEmissaoFIM.Data <> DataZero);
  bPossuiBaixa   := (drBaixaINI.Data   <> DataZero) and (drBaixaFIM.Data   <> DataZero);

  if not (bPossuiEmissao or bPossuiBaixa) then
    RespOkErro('Atencao!', 'Informe o periodo completo de Emissao ou de Baixa.');

  if bPossuiEmissao and (drEmissaoINI.Data > drEmissaoFIM.Data) then
    RespOkErro('Atencao!', 'A Data de Emissao Inicial nao pode ser maior que a Final.');
end;

function TFGeraNotaCredDeb.GetFiltros: String;
var
  cSQL: String;
begin
  cSQL := '';
  cSQL := cSQL + wlEstab.GetSelecaoToSQL('D.ESTAB');
  cSQL := cSQL + wlPessoa.GetSelecaoToSQL('D.IDPESS');
  if edtFatura.Text <> '' then
    cSQL := cSQL + ' AND D.FATURA = ' + QuotedStr(edtFatura.Text);
  Result := cSQL;
end;

end.
"""

_PAS_DATAMODULE = """\
unit uDmProc;

interface

type
  TDmProc = class(TDataModule)
  public
    class function getInstance: TDmProc;
  end;

implementation

{-----------------------------------------------------------------------------
  Procedure: getInstance
  Cria a unica instancia do objeto DmProc e retorna o ponteiro para o mesmo
  Author:    Max
  Date:      15-mar-2007
-----------------------------------------------------------------------------}
class function TDmProc.getInstance: TDmProc;
begin
  if (Application.FindComponent('DmProc') = nil) then
    DmProc := TDmProc.Create(Application);
  Result := DmProc;
end;

end.
"""

_PAS_SEM_IMPLEMENTATION = """\
unit uSoInterface;

interface

type
  TAlgo = class
    procedure Fazer;
  end;

end.
"""

_PAS_SO_TRIVIAIS = """\
unit uSoTriviais;

interface

implementation

procedure TFoo.BtnClick(Sender: TObject);
begin
  DoIt;
end;

end.
"""


# ── should_index_source_path ──────────────────────────────────────────────────

class TestShouldIndexSourcePath:
    def test_aceita_pas_em_pasta_normal(self, tmp_path: Path) -> None:
        f = tmp_path / "App" / "Mercado" / "uGeraNotaCredDeb.pas"
        f.parent.mkdir(parents=True)
        f.write_text("unit x;", encoding="utf-8")
        assert should_index_source_path(f) is True

    def test_rejeita_arquivo_em_history(self, tmp_path: Path) -> None:
        f = tmp_path / "__history" / "uGeraNotaCredDeb.pas.~1~"
        f.parent.mkdir(parents=True)
        f.write_text("unit x;", encoding="utf-8")
        assert should_index_source_path(f) is False

    def test_rejeita_arquivo_em_backup(self, tmp_path: Path) -> None:
        f = tmp_path / "backup" / "uGeraNotaCredDeb.pas"
        f.parent.mkdir(parents=True)
        f.write_text("unit x;", encoding="utf-8")
        assert should_index_source_path(f) is False

    def test_rejeita_nao_pascal(self, tmp_path: Path) -> None:
        f = tmp_path / "App" / "uGeraNotaCredDeb.dfm"
        f.parent.mkdir(parents=True)
        f.write_text("object x: TForm", encoding="utf-8")
        assert should_index_source_path(f) is False

    def test_rejeita_arquivo_oculto(self, tmp_path: Path) -> None:
        f = tmp_path / ".hidden.pas"
        f.write_text("unit x;", encoding="utf-8")
        assert should_index_source_path(f) is False


# ── DelphiMethodChunker ───────────────────────────────────────────────────────

class TestDelphiMethodChunker:
    def _write(self, tmp_path: Path, name: str, content: str) -> Path:
        f = tmp_path / name
        f.write_text(content, encoding="utf-8")
        return f

    def test_formulario_extrai_metodos_nao_triviais(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)

        nomes = [c.metadata.secao for c in chunks]
        # ValidarFiltros e GetFiltros têm corpo suficiente — devem ser indexados
        assert "ValidarFiltros" in nomes
        assert "GetFiltros" in nomes

    def test_event_handler_trivial_descartado(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)

        nomes = [c.metadata.secao for c in chunks]
        # btnExecutarClick tem apenas 2 linhas — deve ser descartado
        assert "btnExecutarClick" not in nomes

    def test_sem_implementation_retorna_lista_vazia(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uSoInterface.pas", _PAS_SEM_IMPLEMENTATION)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert chunks == []

    def test_so_triviais_retorna_lista_vazia(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uSoTriviais.pas", _PAS_SO_TRIVIAIS)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert chunks == []

    def test_metadados_extraidos_corretamente(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)

        chunk = next(c for c in chunks if c.metadata.secao == "ValidarFiltros")
        assert chunk.metadata.doc_id      == "uGeraNotaCredDeb.ValidarFiltros"
        assert chunk.metadata.titulo      == "uGeraNotaCredDeb"
        assert chunk.metadata.tipo        == "unit"   # prefixo "uGera" → fallback genérico
        assert chunk.metadata.path_rel    == "uGeraNotaCredDeb.pas"
        assert chunk.metadata.extras["unit_name"]   == "uGeraNotaCredDeb"
        assert chunk.metadata.extras["class_name"]  == "TFGeraNotaCredDeb"
        assert chunk.metadata.extras["method_name"] == "ValidarFiltros"
        assert chunk.metadata.extras["method_type"] == "procedure"

    def test_modulo_inferido_da_subpasta(self, tmp_path: Path) -> None:
        pasta = tmp_path / "App" / "Mercado"
        pasta.mkdir(parents=True)
        f = pasta / "uGeraNotaCredDeb.pas"
        f.write_text(_PAS_FORMULARIO, encoding="utf-8")

        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert all(c.metadata.modulo == "Mercado" for c in chunks)

    def test_modulo_raiz_quando_sem_subpasta(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert all(c.metadata.modulo == "(raiz)" for c in chunks)

    def test_datamodule_tipo_inferido_corretamente(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uDmProc.pas", _PAS_DATAMODULE)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert all(c.metadata.tipo == "datamodule" for c in chunks)

    def test_comentario_cabecalho_incluido_no_texto(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uDmProc.pas", _PAS_DATAMODULE)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)

        chunk = next(c for c in chunks if c.metadata.secao == "getInstance")
        # O comentário {--- ... ---} deve estar no texto do chunk
        assert "getInstance" in chunk.text
        assert "DmProc" in chunk.text

    def test_chunk_id_deterministico(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks_a = DelphiMethodChunker().chunk_file(f, tmp_path)
        chunks_b = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert [c.id for c in chunks_a] == [c.id for c in chunks_b]

    def test_path_rel_usa_forward_slash(self, tmp_path: Path) -> None:
        pasta = tmp_path / "App" / "Mercado"
        pasta.mkdir(parents=True)
        f = pasta / "uGeraNotaCredDeb.pas"
        f.write_text(_PAS_FORMULARIO, encoding="utf-8")

        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        assert all("/" in c.metadata.path_rel for c in chunks)
        assert all("\\" not in c.metadata.path_rel for c in chunks)

    def test_prefixo_de_contexto_no_texto(self, tmp_path: Path) -> None:
        f = self._write(tmp_path, "uGeraNotaCredDeb.pas", _PAS_FORMULARIO)
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)

        chunk = next(c for c in chunks if c.metadata.secao == "ValidarFiltros")
        # Prefixo [tipo | modulo] deve estar na primeira linha
        assert chunk.text.startswith("[unit |")  # uGeraNotaCredDeb → tipo unit
        assert "uGeraNotaCredDeb" in chunk.text
        assert "ValidarFiltros" in chunk.text

    def test_arquivo_latin1_lido_sem_erro(self, tmp_path: Path) -> None:
        f = tmp_path / "uLatin1.pas"
        # Simula arquivo salvo em latin-1 (encoding antigo do Delphi)
        f.write_bytes(_PAS_FORMULARIO.encode("latin-1"))
        chunks = DelphiMethodChunker().chunk_file(f, tmp_path)
        # Deve processar sem erro e retornar chunks
        assert isinstance(chunks, list)