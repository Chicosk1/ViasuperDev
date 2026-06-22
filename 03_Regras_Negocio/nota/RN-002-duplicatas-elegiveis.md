---
id: RN-002
titulo: "Elegibilidade de registros financeiros para geração de documentos fiscais de ajuste"
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
  - ajuste
  - credito
  - debito
processos_relacionados:
  - PROC-001
  - PROC-003
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-06-19"
---

# Elegibilidade de registros financeiros para geração de documentos fiscais de ajuste

## 1. Definição

Para que um registro financeiro (duplicata, parcela, lançamento de conta a pagar/receber) seja elegível para originar um **documento fiscal de ajuste** (nota de crédito, nota de débito, nota de complemento ou qualquer documento que ajuste base tributária), ele deve possuir ao menos um **valor de variação financeira** diferente de zero: multa, juros, acréscimos ou desconto concedido/obtido. Registros sem nenhuma variação financeira não geram obrigação tributária de ajuste e devem ser excluídos automaticamente do processo de seleção.

Esta regra se aplica a qualquer rotina do ERP que utilize registros financeiros como base para emissão de documentos fiscais de ajuste — incluindo, mas não se limitando a: geração de notas de crédito/débito, ajustes de IBS/CBS, emissão de notas de complemento e geração de documentos de renegociação.

## 2. Contexto

Documentos fiscais de ajuste existem para corrigir ou complementar a carga tributária de operações onde o valor efetivamente pago/recebido diferiu do valor original da nota. Essa diferença surge de encargos financeiros (juros de mora, multa por atraso, acréscimos negociados) ou de benefícios concedidos (descontos comerciais, abatimentos). Um registro financeiro sem nenhuma dessas variações representa uma liquidação exata — o valor pago foi idêntico ao valor cobrado — e, portanto, não há base de ajuste a ser tributada. Incluir esses registros no processo geraria documentos fiscais com valor zero, que são rejeitados pela SEFAZ e causam inconsistências contábeis.

## 3. Condição (Se / Então)

### 3.1 — Registro sem variação financeira (inelegível)
- **Se:** um registro financeiro (baixa de duplicata, lançamento, etc.) não possui nenhum valor maior que zero nos campos: `multa`, `juros`, `acréscimos` e `desconto`;
- **Então:** esse registro **não deve** ser retornado no grid de seleção nem considerado para geração de documento fiscal de ajuste.

### 3.2 — Registro com variação financeira (elegível)
- **Se:** ao menos um dos campos `multa`, `juros`, `acréscimos` ou `desconto` possui valor maior que zero;
- **Então:** o registro é elegível e deve aparecer no grid de seleção para que o usuário decida se deseja gerar o documento de ajuste correspondente.

### 3.3 — Múltiplas baixas parciais de um mesmo registro
- **Se:** um registro financeiro possui mais de uma baixa parcial no período consultado, e cada baixa parcial possui ao menos um valor de variação;
- **Então:** cada baixa parcial deve ser listada como uma **linha separada e independente** no grid, permitindo a seleção individual de quais parcelas gerarão documentos de ajuste.

## 4. Exemplos

### Válido — Duplicata com juros de mora

Duplicata 000123, baixa em 15/06/2026 com atraso de 5 dias:
- Juros: R$ 15,00 | Multa: R$ 5,00 | Acréscimos: R$ 0,00 | Desconto: R$ 0,00
- **Elegível** → aparece no grid para geração de nota de débito (ajuste tributário sobre os encargos).

### Válido — Duplicata com desconto por pagamento antecipado

Duplicata 000456, baixa antecipada:
- Juros: R$ 0,00 | Multa: R$ 0,00 | Acréscimos: R$ 0,00 | Desconto: R$ 30,00
- **Elegível** → aparece no grid para geração de nota de crédito (ajuste tributário sobre o desconto).

### Válido — Duas baixas parciais elegíveis

Duplicata 000789 com 2 baixas parciais:
- Baixa 1: juros R$ 10,00 → linha 1 no grid
- Baixa 2: desconto R$ 5,00 → linha 2 no grid
- Ambas elegíveis, listadas separadamente.

### Inválido — Duplicata quitada no valor exato

Duplicata 001000, baixa total:
- Juros: R$ 0,00 | Multa: R$ 0,00 | Acréscimos: R$ 0,00 | Desconto: R$ 0,00
- **Inelegível** → não deve aparecer no grid. Não há ajuste tributário a ser feito.

## 5. Exceções

- Registros financeiros de **bonificações** (mercadoria sem custo financeiro) possuem tratamento próprio e não seguem esta regra de elegibilidade.
- Em cenários de **renegociação de dívida** onde há geração de novos encargos, os valores dos novos encargos devem ser considerados para elegibilidade, mesmo que os originais sejam zero.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — regra de filtro de consulta aplicada automaticamente pelo sistema ao carregar o grid de seleção de registros financeiros.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.1 | Generalização da regra para abranger qualquer rotina que gere documentos fiscais de ajuste com base em registros financeiros, não apenas notas de crédito/débito. Adição do cenário 3.3 (baixas parciais múltiplas) com exemplos expandidos. |
| 2026-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critério 3.6) |
