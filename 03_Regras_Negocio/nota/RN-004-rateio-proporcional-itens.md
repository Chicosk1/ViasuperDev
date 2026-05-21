---
id: RN-004
titulo: "Rateio proporcional de IBS/CBS nos itens da nota de origem"
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
  - ibs
  - cbs
  - rateio
  - reforma-tributaria
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Rateio proporcional de IBS/CBS nos itens da nota de origem

## 1. Definição

Ao gerar a nota de crédito/débito, os valores informados nas colunas Base IBS à Ajustar e Base CBS à Ajustar devem ser distribuídos proporcionalmente entre os itens da nota fiscal de origem, considerando a participação do valor total de cada item em relação ao valor total da nota.

## 2. Contexto

Uma nota fiscal pode conter múltiplos itens com alíquotas e bases de cálculo distintas. O ajuste de IBS/CBS não pode ser aplicado de forma flat na nota — ele deve ser distribuído por item para que cada um carregue sua parcela proporcional do ajuste, respeitando as reduções de base de cálculo e alíquotas configuradas por item.

## 3. Condição (Se / Então)

- **Se:** o sistema for gerar uma nota de crédito/débito a partir de um registro selecionado.
- **Então:** para cada item da nota de origem, deve calcular:

```
--Cálculo do rateio
```

Os campos Valor Unitário, Valor Total e Base de IBS/CBS da nota gerada devem corresponder aos valores rateados por item.

## 4. Exemplos

### Válido
Nota de origem com 2 itens:
- Item A: valor R$ 600,00 (60% do total de R$ 1.000,00)
- Item B: valor R$ 400,00 (40% do total)

Base IBS à Ajustar = R$ 100,00
- Base IBS Item A = R$ 100,00 × 60% = R$ 60,00
- Base IBS Item B = R$ 100,00 × 40% = R$ 40,00

### Inválido
Aplicar o valor total de Base IBS à Ajustar (R$ 100,00) igualmente em todos os itens sem considerar a proporção.

## 5. Exceções

Itens cujo imposto calculado resulte em valor inferior a R$ 0,01 após o rateio não devem ser incluídos na nota — conforme [[RN-005-item-imposto-menor-centavo]].

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| `ALIQIBSMUN` | Configurada no cadastro de tributação de imposto IVA | Usada para calcular o valor de IBS MUN após o rateio|
| `ALIQIBSUF` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de IBS UF após o rateio |
| `ALIQCBS` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de CBS após o rateio |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2025-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) (critério 3.6) |
