---
id: AG-29135
titulo: "Enviar preços por bandeira para o JETPDV"
tipo: ag
modulo: "pdv"
status: backlog
prioridade: normal
versao_template: "1.0"
contexto_llm: medio
tags:
  - ag
  - pdv
  - carga
  - bandeira
  - preco
processos_impactados: []
rns_impactadas: []
jira: "https://nimitz.atlassian.net/browse/AG-29135"
responsavel: "Oriel Antonio Gaida"
solicitante: ""
sprint: ""
data_criacao: "2026-05-29"
data_limite: ""
data_inicio: ""
data_conclusao: ""
---

# Enviar preços por bandeira para o JETPDV

## 1. Contexto

A rotina de envio de carga para o PDV (Viasuper → Processos → PDV → Envio de cargas para o PDV → Produtos) já envia informações do cadastro de produtos, impostos e preços de venda. Esta AG adiciona suporte ao envio de preços por bandeira de preço, tanto no registro de filial (200 - Lojas) quanto em um novo registro dedicado para preços por bandeira.

## 2. Objetivo

Permitir que, ao enviar a carga de produtos para o PDV, sejam incluídos:
1. O campo Bandeira de Preço no registro da Filial (200 - Lojas).
2. Um novo registro com os preços de venda normais por bandeira de preço (sem ofertas e tabloides, que continuam no registro 12 - Preços).

## 3. Escopo

### Inclui
- Adicionar campo Bandeira de Preço no registro 200 - Lojas, enviado na carga de Conf. Estabelecimentos
- Criar novo registro de exportação de preços por bandeira com estrutura definida
- Preços normais de venda apenas (ofertas e tabloides permanecem no registro 12)

### Não inclui
- Alteração na lógica de envio de ofertas e tabloides (registro 12)
- Alteração em outros registros além do 200 - Lojas e o novo registro de bandeira

## 4. Critérios de Aceite

### 4.1 — Enviar Bandeira de Preço no registro da Filial

- **Dado que** possuímos o registro 200 - Lojas
- **Quando** for realizado o envio da carga de Conf. Estabelecimentos para o PDV
- **Então** deverá ser informado o novo campo: Bandeira de Preço

### 4.2 — Exportar preços por Bandeira

- **Dado que** está sendo enviada uma carga de produtos (Seleção, parcial ou total) para o PDV
- **Quando** o envio for processado
- **Então** deverá ser exportado um novo registro separado do estabelecimento com a seguinte estrutura:

| Sequência | Campo | Tamanho | Decimais | Tipo | Descrição |
| --- | --- | --- | --- | --- | --- |
| 1 | IDBANDEIRA | 10 | 0 | Numérico | Bandeira de preço |
| 2 | ID | 10 | 0 | Numérico | PLU |
| 3 | PRICE | 15 | 3 | Decimal | Preço |
| 4 | START_PRICE | 0 | 0 | Data | Início |

- Somente preços de venda normais neste novo registro
- Ofertas e tabloides continuam sendo enviados no registro 12 - Preços

## 5. Definição de Pronto

- [ ] Campo Bandeira de Preço adicionado ao registro 200 - Lojas
- [ ] Novo registro de preços por bandeira exportado corretamente
- [ ] Carga de seleção, parcial e total validada com preços normais, tabloides e ofertas
- [ ] Tabloides e ofertas continuam no registro 12 sem alteração

## 6. Informações para Testes

- Configurar uma bandeira de preços para o estabelecimento
- Exportar a carga de produtos
- Validar o envio de itens com preço normal, tabloides e ofertas

## 7. Banco de Dados

Não se aplica.
