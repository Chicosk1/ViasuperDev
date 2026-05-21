---
id: RN-002
titulo: "Somente duplicatas com valores de ajuste são elegíveis para geração de notas"
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
  - duplicatas
  - elegibilidade
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Somente duplicatas com valores de ajuste são elegíveis para geração de notas

## 1. Definição

Apenas duplicatas baixadas (total ou parcialmente) que possuam ao menos um dos seguintes valores maior que zero — multa, juros, acréscimos ou desconto — devem ser retornadas no grid da rotina Gerar Notas de Crédito/Débito.

## 2. Contexto

Notas de crédito e débito neste contexto existem para ajustar IBS e CBS decorrentes de variações financeiras ocorridas na baixa (encargos ou descontos). Duplicatas sem esses valores não geram ajuste tributário e não devem poluir o grid.

## 3. Condição (Se / Então)

### 3.1 Exibição de duplicata quando não possuir valor de multa, juros, acréscimos e desconto
- **Se:** uma baixa de duplicata (total ou parcial) não possuir nenhum valor maior que zero nos campos multa, juros, acréscimos e desconto.
- **Então:** essa baixa não deve ser retornada no grid.

### 3.2 Exibição de duplicata quando possuir mais de uma baixa parcial
- **Se:** uma duplicata possui mais de uma baixa parcial no período filtrado, e cada baixa parcial possuir ao menos um valor de ajuste.
- **Então:** cada baixa parcial deve ser listada como uma linha separada no grid.

## 4. Exemplos

### Válido
Duplicata 000123 com duas baixas parciais: baixa 1 com juros de R$ 15,00 e baixa 2 com desconto de R$ 5,00. Ambas são listadas como linhas distintas.

### Válido
Duplicata 000456 com baixa total e multa de R$ 10,00. Listada normalmente.

### Inválido
Duplicata 000789 com baixa total, multa = 0, juros = 0, acréscimos = 0, desconto = 0. Não deve aparecer no grid.

## 5. Exceções

Nenhuma exceção prevista.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — regra de filtro de consulta.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2025-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critério 3.6) |
