---
id: RN-008
titulo: "Cálculo de Sugestão de Compra por Média de Vendas"
tipo: regra-negocio
modulo: "pedido"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - pedido
  - sugestao-compra
  - media-vendas
  - estoque
  - analise-compra
processos_relacionados:
  - PROC-005
  - PROC-007
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Cálculo de Sugestão de Compra por Média de Vendas

## 1. Definição

Quando o método de **Média de Vendas** está habilitado nas rotinas de compra (ou quando o índice de vendas sazonal não está disponível), o sistema calcula a sugestão de quantidade a pedir com base nos campos estatísticos do cadastro do produto: **Média Original**, **Desvio Padrão** e **Média** (geralmente uma média ajustada). Este método fornece uma estimativa estável e suavizada da demanda, adequada para produtos sem sazonalidade pronunciada.

Esta regra se aplica às rotinas de **Análise de Compra**, **Pedido Centralizado** e qualquer outra tela que ofereça cálculo de sugestão de compra no ERP.

## 2. Contexto

A maioria dos produtos de um supermercado apresenta demanda relativamente estável ao longo do tempo. Para esses itens, um cálculo baseado na média histórica de vendas (possivelmente ajustada por desvio padrão para absorver flutuações) é suficiente e computacionalmente mais simples do que o modelo sazonal. Os valores de média e desvio padrão são calculados e atualizados pelo job de banco de dados `CalcEstMedVenda`, que deve estar ativo no **Gerenciador de Tarefas** do ERP.

## 3. Condição (Se / Então)

- **Se:** o usuário seleciona a opção de Média de Vendas na análise de compra, **ou** o produto não possui histórico sazonal suficiente para o cálculo por índice;
- **Então:** o sistema deve:
  1. Recuperar do cadastro do produto os campos: `Média Original`, `Desvio Padrão` e `Média` (campos atualizados pelo job `CalcEstMedVenda`).
  2. Calcular a **Média Diária** de vendas do produto.
  3. Multiplicar pela quantidade de dias de cobertura desejados (baseado no prazo de entrega do fornecedor + estoque de segurança).
  4. Subtrair o saldo atual de estoque disponível para obter a quantidade líquida sugerida.
  5. Apresentar a quantidade resultante como valor de sugestão na coluna do grid.

```
Sugestão = (Média_Diária × Dias_de_Cobertura) - Saldo_Estoque_Atual
```

Onde:
```
Média_Diária = Média_do_Cadastro / Dias_no_Período_de_Referência
```

## 4. Exemplos

### Válido — Produto estável com média bem definida

Produto: Arroz Tipo 1 5kg

| Campo do Cadastro | Valor |
|---|---|
| Média Original | 90 un/mês |
| Desvio Padrão | 5 un |
| Média (ajustada) | 88 un/mês |
| Saldo Atual | 15 un |

Com prazo de cobertura de 30 dias:
- Média Diária = 88 / 30 ≈ 2,93 un/dia
- Sugestão = (2,93 × 30) − 15 = 88 − 15 = **73 unidades**

### Válido — Produto com desvio padrão alto (demanda instável)

O sistema apresenta a sugestão calculada pela média, mas o operador pode consultar o desvio padrão para decidir se aumenta o pedido como margem de segurança.

### Inválido

Calcular a sugestão sem considerar o saldo atual de estoque, resultando em pedidos que causarão excesso de estoque desnecessário.

## 5. Exceções

- Se o job `CalcEstMedVenda` não tiver sido executado recentemente, os campos de média podem estar desatualizados. O sistema não bloqueia a análise, mas as sugestões podem não refletir o consumo atual real.
- Produto sem histórico de vendas (média = 0): a sugestão retornará zero. O operador pode sobrescrever manualmente a quantidade no campo "Qtde. Informada".
- Se o saldo atual for maior que a cobertura calculada, a sugestão deve ser zero (não negativa).

## 6. Parâmetros do ERP Envolvidos

| Parâmetro / Job | Valor esperado | Efeito |
|---|---|---|
| `CalcEstMedVenda` | Executado periodicamente no Gerenciador de Tarefas | Atualiza Média Original, Desvio Padrão e Média no cadastro do produto |
| Campo "Média" no cadastro do produto | Preenchido automaticamente pelo job | Base do cálculo de sugestão |
| Campo "Desvio Padrão" | Preenchido automaticamente pelo job | Indica volatilidade da demanda |
| Prazo de Entrega do Fornecedor | Configurado no vínculo produto × fornecedor | Define os "Dias de Cobertura" no cálculo |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Análise de Compra e Pedido Centralizado |
