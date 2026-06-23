---
id: RN-007
titulo: "Cálculo de Sugestão de Compra por Índice de Vendas (Giro Sazonal)"
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
  - giro-sazonal
  - estoque
  - analise-compra
processos_relacionados:
  - PROC-005
  - PROC-007
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Cálculo de Sugestão de Compra por Índice de Vendas (Giro Sazonal)

## 1. Definição

Quando a opção **"Utilizar Índice de Vendas"** está habilitada nas rotinas de compra, o sistema deve calcular a sugestão de quantidade a pedir com base no **comportamento histórico sazonal** do produto. Este cálculo considera os dados de vendas do mesmo mês do ano nos últimos anos disponíveis e os percentuais de volatilidade recentes para projetar a demanda futura com mais precisão do que uma média simples.

Esta regra se aplica às rotinas de **Análise de Compra** e **Pedido Centralizado** e qualquer outra rotina que ofereça a opção de alternar entre métodos de sugestão.

## 2. Contexto

Produtos com forte sazonalidade (ex: panetone em dezembro, protetor solar no verão) não podem ter sua demanda projetada com precisão a partir de uma média histórica plana. O índice de vendas corrige essa distorção ao segmentar o histórico por mês/período, capturando os picos e vales naturais do comportamento de consumo. O cálculo depende da execução prévia do job de banco de dados `AtGiroSazonal`, que deve estar ativo no **Gerenciador de Tarefas** do ERP.

## 3. Condição (Se / Então)

- **Se:** o usuário habilita "Utilizar Índice de Vendas" ao executar a análise de compra ou sugestão de pedido centralizado;
- **Então:** o sistema deve:
  1. Consultar as vendas reais do produto no mesmo mês/período selecionado, retroagindo até **5 anos** no histórico disponível.
  2. Calcular o índice de participação do mês no total anual de vendas (`Índice Sazonal = Vendas do Mês / Média Mensal Anual`).
  3. Aplicar esse índice sobre a projeção de vendas do período alvo para obter a sugestão.
  4. Considerar os percentuais de volatilidade recentes (ponderação entre histórico antigo e tendência recente) calculados pelo job `AtGiroSazonal`.
  5. Apresentar a quantidade resultante como valor de sugestão na coluna correspondente do grid.

```
Sugestão = Média_Diária_Histórica × Índice_Sazonal_do_Mês × Dias_de_Cobertura_Desejados
```

## 4. Exemplos

### Válido — Produto sazonal com alta demanda no mês selecionado

Produto: Protetor Solar FPS60

| Mês | Vendas Históricas (5 anos atrás) | Índice Calculado |
|---|---|---|
| Janeiro | 120 un | 2.4 (acima da média) |
| Julho | 20 un | 0.4 (abaixo da média) |

Ao executar análise de compra em Janeiro com índice de vendas habilitado:
- O sistema recupera que Janeiro historicamente tem 2.4× a média mensal.
- A sugestão refletirá esse volume elevado, evitando ruptura no pico de verão.

### Inválido

Usar a média aritmética simples de todos os meses do ano para calcular a sugestão de um mês com forte sazonalidade, gerando sugestões defasadas (muito altas fora de época ou muito baixas na época de pico).

## 5. Exceções

- Se o produto não possuir histórico de vendas para o período consultado (produto novo ou recém-cadastrado), o sistema deve apresentar sugestão zero ou utilizar o método alternativo de média de vendas ([[RN-008-sugestao-media-vendas]]).
- Se o job `AtGiroSazonal` não tiver sido executado recentemente, os índices podem estar desatualizados. O sistema não bloqueia a análise, mas a sugestão pode não refletir a sazonalidade real.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro / Job | Valor esperado | Efeito |
|---|---|---|
| `AtGiroSazonal` | Executado periodicamente no Gerenciador de Tarefas | Atualiza os índices sazonais por produto/mês |
| Checkbox "Utilizar Índice de Vendas" | Habilitado pelo usuário na tela de filtros | Ativa o método de cálculo sazonal |
| Período de histórico | Até 5 anos retroativos | Define a janela de dados para cálculo do índice |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Análise de Compra e Pedido Centralizado |
