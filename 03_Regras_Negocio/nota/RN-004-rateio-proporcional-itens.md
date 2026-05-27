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
  - icms
  - rateio
  - reforma-tributaria
  - base-complementar
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-05-22"
---

# Rateio proporcional de IBS/CBS nos itens da nota de origem

## 1. Definição

Ao gerar a nota de crédito/débito, os valores informados nas colunas Base IBS à Ajustar e Base CBS à Ajustar devem ser distribuídos proporcionalmente entre os itens da nota fiscal de origem, considerando a participação do valor total de cada item em relação ao valor total da nota.

O mesmo mecanismo de proporção se aplica ao cálculo da **base complementar** (originada de juros/multas) e a outros cenários de rateio — frete, descontos de produto e despesas acessórias. O que difere entre os cenários é a **etapa final de aplicação do imposto**, conforme detalhado na seção 3.

## 2. Contexto

Uma nota fiscal pode conter múltiplos itens com alíquotas e bases de cálculo distintas. O ajuste de IBS/CBS não pode ser aplicado de forma flat na nota — ele deve ser distribuído por item para que cada um carregue sua parcela proporcional do ajuste, respeitando as reduções de base de cálculo e alíquotas configuradas por item.

Quando o pagamento da duplicata inclui acréscimos (juros e/ou multas), surge um **valor a complementar** que também precisa ser rateado por item antes do cálculo do imposto.

## 3. Condição (Se / Então)

- **Se:** o sistema for gerar uma nota de crédito/débito a partir de um registro selecionado.
- **Então:** para cada item da nota de origem, deve calcular:

**Etapa 1 — Proporção do item (comum a todos os cenários de rateio):**

```
Participação do item (%) = Valor Total do Item / Valor Total da Nota
```

> Esta etapa é idêntica nos cenários de rateio de base complementar, frete, descontos de produto e despesas acessórias.

**Etapa 2 — Aplicação da proporção sobre o valor a ratear:**

Para o rateio da base complementar:

```
Total Pago           = Valor Total da Nota + Juros + Multas
Valor a Complementar = Total Pago − Valor Total da Nota
Base Complementar    = Valor a Complementar × Participação do item (%)
```

Para calcular a alíquota efetiva:
```
Alíquota Efetiva     = Alíquota - (Alíquota * Redução(%))
```
**Etapa 3 — Aplicação do imposto (difere por tipo de imposto):**

| Imposto | Método | Detalhe |
|---|---|---|
| **IBS / CBS** | Redução de **alíquota** | A base de cálculo é considerada como a base complementar; aplica-se uma alíquota efetiva reduzida. |
| **ICMS** | Redução de **base** | A base de cálculo do item é reduzida diretamente antes da aplicação da alíquota cheia. |

Para IBS e CBS, o cálculo final é:

```
Valor IBS do item = Base Complementar IBS × Alíquota Efetiva
Valor CBS do item = Base Complementar CBS × Alíquota Efetiva
```

Os campos Valor Unitário, Valor Total e Base de IBS/CBS da nota gerada devem corresponder aos valores rateados por item.

## 4. Exemplos

### Válido — Rateio de ajuste IBS/CBS

Nota de origem com 2 itens:
- Item A: valor R$ 600,00 (60% do total de R$ 1.000,00)
- Item B: valor R$ 400,00 (40% do total)

Base IBS à Ajustar = R$ 100,00
- Base IBS Item A = R$ 100,00 × 60% = R$ 60,00
- Base IBS Item B = R$ 100,00 × 40% = R$ 40,00

### Válido — Rateio de base complementar (juros/multas)

Item com valor R$ 18,99 em nota de R$ 462,15:
- Participação = 18,99 / 462,15 ≈ 4,10%

Valor a complementar = R$ 8,12 (total pago − valor da nota):
- Base complementar do item = R$ 8,12 × 4,10% ≈ R$ 0,33

### Inválido

Aplicar o valor total de Base IBS à Ajustar (R$ 100,00) igualmente em todos os itens sem considerar a proporção.

## 5. Exceções

Itens cujo imposto calculado resulte em valor inferior a R$ 0,01 após o rateio não devem ser incluídos na nota — conforme [[RN-005-item-imposto-menor-centavo]].

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| `ALIQIBSMUN` | Configurada no cadastro de tributação de imposto IVA | Usada para calcular o valor de IBS MUN após o rateio |
| `ALIQIBSUF` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de IBS UF após o rateio |
| `ALIQCBS` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de CBS após o rateio |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-05-22 | 1.1 | Detalhamento da fórmula de proporção por regra de três; adição do cenário de base complementar (juros/multas) com exemplo numérico (R$ 18,99 / R$ 462,15 → 4,10% × R$ 8,12 = R$ 0,33); generalização da Etapa 1 para frete/descontos/despesas acessórias; distinção IBS/CBS (redução de alíquota) vs ICMS (redução de base) na Etapa 3. |
| 2026-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) (critério 3.6) |