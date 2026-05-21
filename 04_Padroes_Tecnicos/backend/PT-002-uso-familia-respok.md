---
id: PT-002
titulo: "Uso da família RespOk — mensagens e validações ao usuário"
tipo: padrao-tecnico
modulo: "global"
linguagem: "delphi"
status: ativo
versao_template: "1.0"
contexto_llm: medio
tags:
  - padrao-tecnico
  - delphi
  - global
  - respok
  - validacao
  - mensagens
  - ui
processos_relacionados:
  - PROC-001
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Uso da família RespOk — mensagens e validações ao usuário

## 1. Objetivo

Definir qual função da família `BResp` usar para cada tipo de interação com o usuário — validações bloqueantes, confirmações, avisos e erros — garantindo consistência visual e comportamento correto de fluxo (interrupção vs. continuação).

## 2. Padrão Definido

### 2.1 Mapa de funções por intenção

| Intenção | Função correta | Interrompe execução? | Retorno |
|---|---|---|---|
| Validação bloqueante (erro de entrada) | `RespOkErro` | Sim — possui `Abort` internamente | `void` |
| Aviso informativo — fluxo continua | `RespOk` ou `RespOKinfo` | Não | `void` |
| Confirmação Sim/Não | `RespSN` | Não — depende do retorno `Boolean` | `Boolean` |
| Confirmação Sim/Não/Cancelar | `RespSNC` | Não — depende do retorno `Integer` | `Integer` (1=Sim, 2=Não, 3=Cancelar) |
| Mensagem com detalhe expansível | `RespOkDetalhe` | Não | `void` |
| Validação que deve focar um componente e abortar | `RespOkAbort(oComp, Titulo, Msg)` | **Sim — levanta `Abort`** | `void` |

### 2.2 RespOkErro

Usado dentro de procedimentos de validação que controlam o fluxo externamente (ex: `ValidarFiltros` lança exceção via `RespOkErro` que internamente chama `Abort`):

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

`RespOkErro` exibe a mensagem com ícone de erro e **levanta `Abort`** — o código após a chamada não é executado.

### 2.3 RespOkAbort

Quando a validação deve retornar o foco ao campo inválido antes de abortar:

```pascal
if edtValor.Text = '' then
  RespOkAbort(edtValor, 'Atenção!', 'O campo Valor é obrigatório.');
// código abaixo NÃO é executado — Abort foi levantado
```

### 2.4 RespSN

```pascal
if not RespSN('Confirmar', 'Deseja gerar as notas selecionadas?') then
  Exit;
// prossegue somente se o usuário clicar em Sim
```

### 2.5 RespOk

```pascal
RespOk('Atenção', 'Nenhum registro encontrado para os filtros informados.');
// fluxo CONTINUA após a mensagem
```

### 2.6 RespOkDetalhe

Para erros técnicos onde o detalhe ajuda o suporte mas não deve poluir a mensagem principal:

```pascal
RespOkDetalhe(
  'Erro ao gerar nota',               // título
  'Não foi possível gerar a nota.',   // mensagem principal
  'Detalhe técnico',                  // título do detalhe
  E.Message,                          // conteúdo do detalhe
  1,                                  // TipoMSG: 1=Erro
  False                               // detalhe fechado por padrão
);
```

## 3. Anti-padrão (o que NÃO fazer)

**Não usar `ShowMessage` diretamente — quebra o padrão visual:**

```pascal
// ERRADO
ShowMessage('Informe o período!');

// CERTO
RespOkErro('Atenção!', 'Informe o período de emissão ou de baixa.');
```

**Não confundir `RespOk` (aviso, não aborta) com `RespOkErro` (aborta):**

```pascal
// ERRADO: RespOk não aborta — código continua executando após a mensagem
RespOk('Atenção!', 'Configuração de documento inválida.');
GerarNotas; // ← executa mesmo após a mensagem de erro!

// CERTO: RespOkErro levanta Abort
RespOkErro('Atenção!', 'Configuração de documento inválida.');
// GerarNotas não é executada
```

**Não implementar validações com `if/else` encadeados após `RespOkErro` — o Abort já interrompe:**

```pascal
// ERRADO: código morto após RespOkErro
if not bValido then
begin
  RespOkErro('Atenção!', 'Campo inválido.');
  Exit; // ← desnecessário, Abort já foi levantado
end;

// CERTO
if not bValido then
  RespOkErro('Atenção!', 'Campo inválido.');
```

## 4. Quando Aplicar

- **Sempre** que precisar interagir com o usuário via mensagem ou confirmação — nunca usar `ShowMessage` diretamente.
- Validações de filtros obrigatórios e consistência de dados: `RespOkErro`.
- Confirmações antes de operações destrutivas ou irreversíveis: `RespSN`.
- Avisos informativos onde o fluxo deve continuar: `RespOk` ou `RespOKinfo`.
- Erros técnicos com stack trace ou detalhe interno: `RespOkDetalhe` com `TipoMSG = 1`.

## 5. Exceções Permitidas

- `RespOkWithTimer`: aceito para mensagens temporárias que fecham automaticamente (ex: feedback de processo concluído sem exigir interação do usuário).
- `RespSNWithTimer`: aceito para confirmações com timeout onde a ação padrão deve ser executada automaticamente após o tempo (ex: operações batch sem usuário presente).

## 6. Referência de tipos de mensagem (`TipoMSG` em `RespOkDetalhe`)

| Valor | Tipo | Ícone |
|---|---|---|
| `0` | Info (padrão) | Informação |
| `1` | Erro | Erro |
| `2` | Atenção | Aviso |
| `3` | Pergunta | Interrogação |

## 7. Processos que Usam Este Padrão

- [[PROC-001-gerar-notas-credito-debito-massa]]