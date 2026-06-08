---
id: RN-003
titulo: "Cálculo automático da Base IBS/CBS a Ajustar"
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
  - calculo
  - reforma-tributaria
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-05-21"
---

# Cálculo automático da Base IBS/CBS a Ajustar

## 1. Definição

Ao listar as duplicatas no grid, o sistema deve preencher automaticamente as colunas Base IBS à Ajustar e Base CBS à Ajustar com o resultado da fórmula: Juros + Multa + Acréscimos − Desconto.

## 2. Contexto

IBS e CBS incidem sobre o valor efetivamente recebido/pago. Quando uma baixa inclui encargos (juros, multa, acréscimos) ou descontos, a base tributável deve ser ajustada por esse delta. A fórmula unifica os acréscimos e subtrai os descontos para apurar o valor líquido de ajuste.

## 3. Condição (Se / Então)

- **Se:** o sistema listar uma baixa de duplicata no grid.
- **Então:** deve calcular e preencher automaticamente:

```
Base IBS à Ajustar = Juros + Multa + Acréscimos - Desconto
Base CBS à Ajustar = Juros + Multa + Acréscimos - Desconto
```

- **Senão:** os campos ficam com valor zero quando todos os componentes são zero (o que não deveria ocorrer, pois essa baixa seria filtrada pela [[RN-002-duplicatas-elegiveis]]).

O usuário pode editar manualmente esses valores após o preenchimento automático.

## 4. Exemplos

### Válido
Baixa com juros = R$ 50,00, multa = R$ 10,00, acréscimos = R$ 0,00, desconto = R$ 5,00.
- Base IBS à Ajustar = 50 + 10 + 0 − 5 = **R$ 55,00**
- Base CBS à Ajustar = 50 + 10 + 0 − 5 = **R$ 55,00**

### Válido
Baixa com desconto = R$ 20,00 e sem encargos.
- Base IBS à Ajustar = 0 + 0 + 0 − 20 = **−R$ 20,00** (nota de crédito)
- Base CBS à Ajustar = **−R$ 20,00**

### Inválido
Sistema não preencher automaticamente os campos e fazer o usuário calcular manualmente.

## 5. Exceções

O usuário pode alterar manualmente os valores calculados antes de clicar em Próximo, para casos onde o ajuste desejado difere do cálculo automático.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — cálculo fixo baseado nos valores da baixa.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critérios 3.7 e 3.8) |
