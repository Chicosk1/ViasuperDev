---
id: RN-004
titulo: "Rateio proporcional de valores nos itens do documento"
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
  - pedido
  - nota-fiscal
  - ctrc
  - cupom
  - importacao-xml
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-06-11"
---

# Rateio proporcional de valores nos itens do documento

## 1. Definição

Sempre que um valor global precisar ser distribuído entre os itens de um documento fiscal ou comercial, esse valor deve ser rateado proporcionalmente, considerando a participação do valor total de cada item em relação ao valor total do documento.

Este mecanismo se aplica a qualquer cenário em que exista um montante que não pertença a um único item, mas sim ao documento como um todo. Os cenários mais comuns incluem:

- **Impostos ajustados** (IBS, CBS, ICMS): base de ajuste distribuída pelos itens da nota de origem.
- **Frete, seguro e despesas acessórias**: valor global no documento rateado pelos itens.
- **Desconto global/comercial**: desconto concedido no cabeçalho do documento distribuído por item.
- **Base complementar** (juros/multas): valor a complementar decorrente de encargos financeiros rateado pelos itens da nota de origem.

A regra se aplica em diversas rotinas do ERP, incluindo, mas não se limitando a: pedidos de venda, pedidos de compra, pedidos centralizados, notas de compra, notas de venda, notas de serviço, CTRC, geração de notas de crédito/débito, importação de XML (NF-e de fornecedor) e cupons fiscais (NFC-e).

## 2. Contexto

Um documento fiscal ou comercial pode conter múltiplos itens com alíquotas, bases de cálculo e valores distintos. Valores globais registrados no cabeçalho do documento — como frete, desconto geral, seguro, despesas acessórias ou ajustes de imposto — não podem ser aplicados de forma igualitária (flat) entre os itens. Cada item deve receber sua parcela proporcional, preservando a coerência tributária e contábil da operação.

## 3. Condição (Se / Então)

- **Se:** o sistema precisar distribuir um valor global entre os itens de um documento.
- **Então:** para cada item do documento, deve calcular:

**Etapa 1 — Proporção do item (comum a todos os cenários de rateio):**

```
Participação do item (%) = Valor Total do Item / Valor Total do Documento
```

> Esta proporção é a base de todos os cenários de rateio descritos a seguir.

---

**Etapa 2 — Aplicação da proporção sobre o valor a ratear:**

**Cenário A — Rateio de ajuste de imposto (ex: IBS/CBS na geração de notas de crédito/débito):**

```
Valor Rateado por Item = Valor Global a Ratear × Participação do item (%)
```

**Cenário B — Rateio de base complementar (ex: juros/multas na geração de notas de crédito/débito):**

```
Total Pago           = Valor Total do Documento + Juros + Multas
Valor a Complementar = Total Pago − Valor Total do Documento
Base Complementar    = Valor a Complementar × Participação do item (%)
```

**Cenário C — Rateio de frete, seguro ou despesas acessórias (ex: pedidos de venda/compra, importação de XML):**

```
Valor Rateado por Item = Valor Global (Frete/Seguro/Despesa) × Participação do item (%)
```

**Cenário D — Rateio de desconto global (ex: pedidos, cupons, importação de XML):**

```
Desconto por Item = Desconto Global × Participação do item (%)
```

---

**Etapa 3 — Aplicação do imposto sobre o valor rateado (difere por tipo de imposto):**

| Imposto | Método | Detalhe |
|---|---|---|
| **IBS / CBS** | Redução de **alíquota** | A base de cálculo é o valor rateado; aplica-se uma alíquota efetiva reduzida. |
| **ICMS** | Redução de **base** | A base de cálculo do item é reduzida diretamente antes da aplicação da alíquota cheia. |

Para calcular a alíquota efetiva de IBS/CBS:
```
Alíquota Efetiva = Alíquota − (Alíquota × Redução (%))
```

Para IBS e CBS, o cálculo final é:
```
Valor IBS do item = Base Rateada IBS × Alíquota Efetiva
Valor CBS do item = Base Rateada CBS × Alíquota Efetiva
```

> A Etapa 3 só se aplica quando o rateio impacta a base de cálculo de um imposto. Para frete, seguro e descontos sem reflexo tributário direto, a Etapa 2 já encerra o cálculo.

## 4. Exemplos

### Válido — Rateio de ajuste IBS/CBS (Geração de Notas de Crédito/Débito)

Rotina: **Geração de Notas de Crédito e Débito em Massa**

Nota de origem com 2 itens (total R$ 1.000,00):
- Item A: R$ 600,00 → Participação = 60%
- Item B: R$ 400,00 → Participação = 40%

Base IBS à Ajustar = R$ 100,00:
- Base IBS Item A = R$ 100,00 × 60% = R$ 60,00
- Base IBS Item B = R$ 100,00 × 40% = R$ 40,00

---

### Válido — Rateio de base complementar por juros/multas (Geração de Notas de Crédito/Débito)

Rotina: **Geração de Notas de Crédito e Débito em Massa**

Item com valor R$ 18,99 em nota de origem de R$ 462,15:
- Participação = 18,99 / 462,15 ≈ 4,10%

Valor a complementar = R$ 8,12 (total pago − valor da nota):
- Base complementar do item = R$ 8,12 × 4,10% ≈ R$ 0,33

---

### Válido — Rateio de frete global pelos itens (Pedido de Venda / Nota de Compra)

Rotinas: **Pedido de Venda**, **Nota de Compra**, **Importação de XML (NF-e de fornecedor)**

Pedido com 2 itens (total R$ 500,00) e frete global de R$ 50,00:
- Item A: R$ 300,00 → Participação = 60% → Frete = R$ 30,00
- Item B: R$ 200,00 → Participação = 40% → Frete = R$ 20,00

---

### Válido — Rateio de desconto global pelos itens (Pedido de Venda / Cupom Fiscal)

Rotinas: **Pedido de Venda**, **Cupom Fiscal (NFC-e)**

Documento com 3 itens (total R$ 200,00) e desconto global de R$ 20,00:
- Item A: R$ 100,00 → Participação = 50% → Desconto = R$ 10,00
- Item B: R$ 60,00  → Participação = 30% → Desconto = R$ 6,00
- Item C: R$ 40,00  → Participação = 20% → Desconto = R$ 4,00

---

### Inválido

Aplicar o valor global (ex: Base IBS à Ajustar de R$ 100,00 ou frete de R$ 50,00) **igualmente** em todos os itens, sem considerar a proporção de cada um.

## 5. Exceções

Itens cujo imposto calculado resulte em valor inferior a R$ 0,01 após o rateio não devem ser incluídos no documento gerado — conforme [[RN-005-item-imposto-menor-centavo]].

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| `ALIQIBSMUN` | Configurada no cadastro de tributação de imposto IVA | Usada para calcular o valor de IBS MUN após o rateio |
| `ALIQIBSUF` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de IBS UF após o rateio |
| `ALIQCBS` | Configurada no cadastro tributação de imposto IVA | Usada para calcular o valor de CBS após o rateio |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-11 | 1.2 | Generalização da regra para abranger múltiplos tipos de documentos e rotinas (pedidos, notas, CTRC, cupons, importação de XML). Adição dos cenários C (frete/seguro/despesas) e D (desconto global) com exemplos práticos referenciando rotinas específicas. |
| 2026-05-22 | 1.1 | Detalhamento da fórmula de proporção por regra de três; adição do cenário de base complementar (juros/multas) com exemplo numérico (R$ 18,99 / R$ 462,15 → 4,10% × R$ 8,12 = R$ 0,33); generalização da Etapa 1 para frete/descontos/despesas acessórias; distinção IBS/CBS (redução de alíquota) vs ICMS (redução de base) na Etapa 3. |
| 2026-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) (critério 3.6) |