---
id: ARQ-001
titulo: "Arquitetura — Tela de Filtros e Listagem (uGeraNotaCredDeb)"
tipo: arquitetura
modulo: "nota"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - arquitetura
  - nota
  - nfe
  - delphi
  - ibs
  - cbs
criterios_decisao:
  - "Reutilizar padrão TFFormProc já consolidado no sistema"
  - "ClientDataSet para manipulação local dos dados do grid antes de commitar"
  - "Consultas nomeadas via QueryPegaData para centralizar SQL no servidor"
processos_relacionados:
  - PROC-001
rns_relacionadas:
  - RN-001
  - RN-002
  - RN-003
substitui: ""
substituido_por: ""
data_criacao: "2026-05-21"
data_revisao: "2026-05-21"
---

# Arquitetura — Tela de Filtros e Listagem (uGeraNotaCredDeb)

## 1. Objetivo

Documentar a estrutura, responsabilidades e decisões de implementação da unit `uGeraNotaCredDeb.pas`, que implementa a Tela 1 do processo [[PROC-001-gerar-notas-credito-debito-massa]]: filtros de busca, listagem de duplicatas elegíveis e seleção de registros para geração de notas.

## 2. Decisão

Utilizamos `TFFormProc` como classe base (padrão do sistema) e `TVsClientDataSet` para carregar e manipular localmente os dados do grid, permitindo edição das colunas `Base IBS à Ajustar` e `Base CBS à Ajustar` sem consultar o banco. A seleção de consulta SQL é feita em tempo de execução via `DefinirParametros`, alternando entre as queries `SEL_MERC_GERANOTACREDDEB_DUPREC` e `SEL_MERC_GERANOTACREDDEB_DUPPAG` conforme o radio group selecionado.

## 3. Componentes

| Componente | Tipo | Responsabilidade |
|---|---|---|
| `uGeraNotaCredDeb.pas` | Unit Delphi (TFFormProc) | Tela 1 — filtros, grid e seleção de registros |
| `cdsGeraNotaCredDeb` | TVsClientDataSet | Armazena localmente os dados retornados pela query |
| `dsGeraNotaCredDeb` | TDataSource | Conecta o CDS ao grid e aos filtros de data |
| `SEL_MERC_GERANOTACREDDEB_DUPREC` | Query nomeada (servidor) | Retorna baixas de duplicatas a receber com valores de ajuste |
| `SEL_MERC_GERANOTACREDDEB_DUPPAG` | Query nomeada (servidor) | Retorna baixas de duplicatas a pagar com valores de ajuste |
| `DUPREC` | Tabela Oracle | Duplicatas a receber |
| `DUPPAG` | Tabela Oracle | Duplicatas a pagar |
| `DUPRECACERFIN` / `ACERDRE` | Tabelas Oracle | Baixas de duplicatas a receber (juros, multa, desconto, acréscimo) |
| `DUPPAGACERFIN` / `ACERDPA` | Tabelas Oracle | Baixas de duplicatas a pagar |
| `NOTAITEM` | Tabela Oracle | Itens da nota fiscal de origem |
| `NOTAITEMIMPOSTOIVA` | Tabela Oracle | Valores de IBS/CBS por item da nota de origem |
| `NOTAACERFIN` / `ACERFIN` | Tabelas Oracle | Vínculo entre nota fiscal e baixas financeiras |
| `NOTACONF` | Tabela Oracle | Configuração de documento (finalidade 5/6) |
| `PESSOADOC` | Tabela Oracle | Cadastro de pessoas (lookup) |
| `FILIAL` | Tabela Oracle | Cadastro de estabelecimentos (lookup) |
| `PORTADOR` | Tabela Oracle | Cadastro de portadores (lookup) |

## 4. Código de Referência

### 4.1 Seleção dinâmica de consulta por tipo de duplicata

```pascal
procedure TFGeraNotaCredDeb.DefinirParametros;
begin
  if rbDuplicataReceber.Checked then
  begin
    FConsulta := 'SEL_MERC_GERANOTACREDDEB_DUPREC';
    SetTabelaFiltro('DUPREC');
  end
  else if rbDuplicataPagar.Checked then
  begin
    FConsulta := 'SEL_MERC_GERANOTACREDDEB_DUPPAG';
    SetTabelaFiltro('DUPPAG');
  end;
end;
```

`FConsulta` é uma `String` privada que armazena o nome da query nomeada a ser executada. `SetTabelaFiltro` ajusta o `DireitoTabela` dos campos `edtDuplicata` e `edtFatura` para que o lookup de direitos funcione corretamente conforme o tipo selecionado.

### 4.2 Validação de filtros mínimos

```pascal
procedure TFGeraNotaCredDeb.ValidarFiltros;
var
  bPossuiEmissao, bPossuiBaixa: Boolean;
begin
  bPossuiEmissao := (drEmissaoINI.Data <> DataZero) and (drEmissaoFIM.Data <> DataZero);
  bPossuiBaixa   := (drBaixaINI.Data   <> DataZero) and (drBaixaFIM.Data   <> DataZero);

  if not (bPossuiEmissao or bPossuiBaixa) then
    RespOkErro('Atenção!', 'Para realizar a consulta, informe o período completo de Emissão ou de Baixa.');

  if bPossuiEmissao and (drEmissaoINI.Data > drEmissaoFIM.Data) then
    RespOkErro('Atenção!', 'A Data de Emissão Inicial não pode ser maior que a Final.');

  if bPossuiBaixa and (drBaixaINI.Data > drBaixaFIM.Data) then
    RespOkErro('Atenção!', 'A Data de Baixa Inicial não pode ser maior que a Final.');
end;
```

`RespOkErro` interrompe a execução com exceção. Três validações encadeadas: 
1. Ao menos um intervalo completo 
2. Consistência interna do intervalo de emissão 
3. Consistência interna do intervalo de baixa.

### 4.3 Construção dinâmica de filtros SQL

```pascal
function TFGeraNotaCredDeb.GetFiltros: String;
var
  cSQL: String;
begin
  cSQL := '';
  cSQL := cSQL + wlEstab.GetSelecaoToSQL('D.ESTAB');
  cSQL := cSQL + wlPessoa.GetSelecaoToSQL('D.IDPESS');
  cSQL := cSQL + wlPortador.GetSelecaoToSQL('D.IDPORTADOR');

  if edtFatura.Text <> '' then
    cSQL := cSQL + ' AND D.FATURA = ' + QuotedStr(edtFatura.Text);

  if (edtDuplicata.Text <> '') and rbDuplicataReceber.Checked then
    cSQL := cSQL + ' AND D.DUPREC = ' + QuotedStr(edtDuplicata.Text)
  else if (edtDuplicata.Text <> '') and rbDuplicataPagar.Checked then
    cSQL := cSQL + ' AND D.DUPPAG = ' + QuotedStr(edtDuplicata.Text);

  if (drEmissaoINI.Data <> DataZero) and (drEmissaoFIM.Data <> DataZero) then
    cSQL := cSQL + ' AND D.DTEMISSAO BETWEEN :DTINIEMI AND :DTFIMEMI';

  if (drBaixaINI.Data <> DataZero) and (drBaixaFIM.Data <> DataZero) then
    cSQL := cSQL + ' AND B.DTBAIXA BETWEEN :DTINIBX AND :DTFIMBX';

  Result := cSQL;
end;
```

O alias `D` referencia a tabela de duplicatas (`DUPREC` ou `DUPPAG`) e `B` referencia a tabela de baixas. Os filtros de data usam parâmetros nomeados (`:DTINIEMI`, `:DTFIMEMI`, `:DTINIBX`, `:DTFIMBX`) passados via `QueryPegaData`.

### 4.4 Execução da consulta

```pascal
procedure TFGeraNotaCredDeb.CarregarNotaCredDeb;
begin
  cdsGeraNotaCredDeb.Close;
  cdsGeraNotaCredDeb.ClearFilter;

  cdsGeraNotaCredDeb.Data := DmConexao.QueryPegaData(
    FConsulta, '*',
    ['?',      '1:s',                  GetFiltros,
     'P', 'DTINIEMI', DataNull(drEmissaoINI.Data),
     'P', 'DTFIMEMI', DataNull(drEmissaoFIM.Data),
     'P', 'DTINIBX',  DataNull(drBaixaINI.Data),
     'P', 'DTFIMBX',  DataNull(drBaixaFIM.Data)],
    [ftString, ftDate, ftDate, ftDate, ftDate],
    [1000, 0, 0, 0, 0]);
end;
```

`QueryPegaData` recebe o nome da query nomeada, injeta o fragmento SQL dinâmico de `GetFiltros` via placeholder `'?'` / `'1:s'`, e passa os parâmetros de data com `DataNull` (converte `DataZero` para `NULL`). O limite de retorno é `1000` registros.

## 5. Alternativas Descartadas

| Alternativa | Motivo da rejeição |
|---|---|
| Query fixa com todos os filtros opcionais via `COALESCE` | Gerava plano de execução ineficiente no Oracle para filtros de alta seletividade (ex: duplicata específica) |
| Dois formulários separados (receber / pagar) | Duplicação de código; a diferença se resume à query e ao campo de duplicata — resolvida por `DefinirParametros` |

## 6. Consequências

### Positivas
- Troca de contexto (receber ↔ pagar) sem recarregar o formulário — apenas `DefinirParametros` é chamado.
- Filtros dinâmicos via `GetFiltros` permitem adicionar novos critérios sem alterar a assinatura da query nomeada.
- `TVsClientDataSet` permite edição local de `TOTAL_AJUSTAR` sem consultar o banco.

### Negativas / Riscos
- Limite de 1000 registros hardcoded em `CarregarNotaCredDeb` — empresas com alto volume de baixas diárias podem atingir o limite silenciosamente. Considerar exibir aviso quando o retorno atingir o limite.
- As colunas `Base IBS à Ajustar` e `Base CBS à Ajustar` compartilham o mesmo `DataBinding.FieldName = 'TOTAL_AJUSTAR'` no grid. Qualquer edição em uma coluna reflete na outra. Se as bases precisarem ser independentes no futuro, o CDS precisará de dois campos distintos.
- `GetFiltros` concatena `QuotedStr` diretamente para `edtFatura` e `edtDuplicata` — injeção de SQL possível se os campos não tiverem validação de caracteres no nível do componente `TVsEditRight`.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2025-05-21 | 1.0 | Criação a partir do fonte `uGeraNotaCredDeb.pas` [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) |
