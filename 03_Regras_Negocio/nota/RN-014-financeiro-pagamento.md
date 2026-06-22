---
id: RN-014
titulo: "Obrigatoriedade e Formas de Pagamento em Documentos Fiscais"
tipo: regra-negocio
modulo: "fiscal"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - fiscal
  - financeiro
  - pagamento
  - duplicatas
  - nota-fiscal
  - pedido
processos_relacionados:
  - PROC-002
  - PROC-003
  - PROC-004
  - PROC-008
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Obrigatoriedade e Formas de Pagamento em Documentos Fiscais

## 1. Definição

Todo documento fiscal de entrada ou pedido de compra no ERP deve ter seu **bloco financeiro** devidamente configurado antes da finalização: as duplicatas (parcelas) devem ser geradas com datas de vencimento, formas de pagamento e valores compatíveis com o total do documento. O sistema valida a consistência entre o valor total do documento e o somatório das parcelas antes de permitir o salvamento.

Esta regra se aplica a notas fiscais de entrada, pedidos de compra, recepções e qualquer documento do ERP que gere obrigação financeira (contas a pagar ou receber).

## 2. Contexto

A correta geração das parcelas financeiras é o que alimenta o contas a pagar do ERP e permite o controle de fluxo de caixa. Uma nota fiscal sem parcelas financeiras ou com valores inconsistentes impede a conciliação bancária, o pagamento correto ao fornecedor e a apuração fiscal do período. O ERP oferece ferramentas para gerar o parcelamento automaticamente a partir da data de emissão e do prazo de pagamento negociado, mas também permite ajuste manual.

## 3. Condição (Se / Então)

- **Se:** o usuário tenta salvar um documento fiscal ou pedido de compra;
- **Então:**
  1. O sistema verifica se existe ao menos **uma parcela** gerada na aba de pagamento/financeiro.
  2. Valida que o **somatório das parcelas** é igual ao valor total do documento (com tolerância mínima de centavos conforme [[RN-005-item-imposto-menor-centavo]]).
  3. Valida que cada parcela possui:
     - **Data de vencimento** preenchida e válida (data futura ou igual à emissão).
     - **Forma de pagamento** selecionada (boleto, cheque, depósito, etc.).
     - **Valor** positivo e maior que zero.
  4. Se qualquer validação falhar, o sistema bloqueia o salvamento e exibe mensagem indicando a inconsistência financeira.
  5. Se aprovado, as parcelas são gravadas no módulo de **Contas a Pagar** automaticamente, vinculadas ao CNPJ do fornecedor e ao número do documento.

**Geração Automática de Parcelas:**
- **Se:** o usuário informa o número de parcelas e a data do primeiro vencimento e clica em "Gerar Previsões";
- **Então:** o sistema distribui o valor total do documento igualmente (ou conforme configuração de arredondamento) entre as parcelas, com intervalos regulares de dias entre os vencimentos.

## 4. Exemplos

### Válido — NF de R$ 3.000,00 com 3 parcelas mensais

| Parcela | Vencimento | Forma | Valor |
|---|---|---|---|
| 1/3 | 30/07/2026 | Boleto | R$ 1.000,00 |
| 2/3 | 30/08/2026 | Boleto | R$ 1.000,00 |
| 3/3 | 30/09/2026 | Boleto | R$ 1.000,00 |

Somatório = R$ 3.000,00 = Total da NF ✓

### Inválido — Parcelas com somatório divergente

NF de R$ 3.000,00 com parcelas totalizando R$ 2.900,00:
- Sistema bloqueia o salvamento e exibe: *"Valor das parcelas diverge do total do documento."*

### Inválido — Parcela sem forma de pagamento

Parcela com data e valor definidos, mas campo "Forma de Pagamento" em branco:
- Sistema bloqueia o salvamento e exibe: *"Informe a forma de pagamento para as parcelas."*

## 5. Exceções

- Documentos do tipo **Bonificação** (mercadoria sem custo financeiro) podem ter o bloco de pagamento com valor zero. A forma de pagamento neste caso é parametrizada na configuração do tipo de documento.
- Notas fiscais com **desconto no ato** (pagamento à vista com desconto) podem ter a data de vencimento igual à data de emissão.
- Em casos de importação de XML (NF-e), as duplicatas do XML do fornecedor são automaticamente importadas para o bloco financeiro, mas o usuário pode ajustá-las antes de salvar.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Formas de Pagamento | Configurações > Financeiro > Formas de Pagamento | Define as opções disponíveis para seleção nas parcelas |
| Configuração do Documento | Configurações > Documentos | Define se o documento exige bloco financeiro obrigatório |
| Tolerância de arredondamento | Configurações > Gerais > Fiscal | Define tolerância em centavos na conferência de somatório |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Importação NF-e, Nota Fiscal, Pedidos e Recepção de Pedidos |
