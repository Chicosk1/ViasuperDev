---
id: IDX-nota
titulo: "Índice — Nota Fiscal"
tipo: indice
modulo: "nota"
status: ativo
versao_template: "1.0"
contexto_llm: baixo
tags:
  - indice
  - nota
  - nfe
  - reforma-tributaria
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Índice — Nota Fiscal e Reforma Tributária

<!--
  Este arquivo é navegação, não conhecimento.
  contexto_llm: baixo = o indexer.py exclui este arquivo da vetorização.
  Atualize manualmente ao criar novos documentos no módulo.
-->

## Processos

| ID | Título | Status |
|---|---|---|
| [[PROC-001-gerar-notas-credito-debito-massa]] | Geração de Notas de Crédito e Débito em Massa | ativo |

## Regras de Negócio

| ID | Título | Criticidade |
|---|---|---|
| [[RN-001-filtro-data-obrigatorio]] | Filtro de intervalo de datas obrigatório na busca de duplicatas | media |
| [[RN-002-duplicatas-elegiveis]] | Somente duplicatas com valores de ajuste são elegíveis para geração de notas | alta |
| [[RN-003-calculo-base-ajuste-ibs-cbs]] | Cálculo automático da Base IBS/CBS a Ajustar | alta |
| [[RN-004-rateio-proporcional-itens]] | Rateio proporcional de IBS/CBS nos itens da nota de origem | alta |
| [[RN-005-item-imposto-menor-centavo]] | Itens com imposto calculado inferior a R$ 0,01 não são incluídos na nota gerada | media |
| [[RN-006-configuracao-documento-finalidade]] | Configuração de documento deve ter finalidade Nota de Crédito ou Nota de Débito | media |

## Arquiteturas

| ID | Título | Status |
|---|---|---|
| [[ARQ-001-unit-gera-nota-cred-deb-tela-filtros]] | Arquitetura — Tela de Filtros e Listagem (uGeraNotaCredDeb) | ativo |

## Padrões Técnicos

| ID | Título | Status |
|---|---|---|
| [[PT-001-uso-querypegadata-querypegacampo]] | Uso de QueryPegaData e QueryPegaCampo | ativo |
| [[PT-002-uso-familia-respok]] | Uso da família RespOk — mensagens e validações ao usuário | ativo |

## Glossário

- [[GLOS-nota]]