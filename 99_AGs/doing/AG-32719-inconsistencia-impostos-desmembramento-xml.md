---
ag: AG-32719
titulo: Inconsistência nos impostos ao gravar nota fiscal após desmembramento de produtos na importação de XML
modulo: NF-e / Importação NF-e
processos_impactados:
  - Importação NF-e
  - Conferência de Pedido via XML da NFe v.2
  - Geração de Nota Fiscal de Entrada (retaguarda)
rns_impactadas: []
tags:
  - bug
  - impostos
  - desmembramento
  - xml
  - icms
  - pis
  - cofins
jira: https://nimitz.atlassian.net/browse/AG-32719
status: backlog
---

# AG-32719 — Inconsistência nos impostos ao gravar nota fiscal após desmembramento de produtos na importação de XML

## 1. Objetivo

Corrigir o comportamento da aba "ICMS, PIS e COFINS" na rotina de Importação NF-e para que, após o desmembramento de um item do XML em dois ou mais produtos distintos, os registros de impostos sejam recalculados e reconstruídos automaticamente com rateio proporcional pelo valor financeiro de cada item resultante.

## 2. Contexto

Identificado que ao realizar o desmembramento de itens na rotina de Importação NF-e, ao conferirmos a aba de ICMS, PIS e COFINS, os itens exibidos não estão sendo atualizados conforme o desmembramento executado. Isso gera um comportamento inesperado de desconexão entre as abas, causando inconsistências entre os totais acumulados dos impostos e o somatório individualizado dos itens resultantes do desmembramento.

**Rotina afetada:** Viasuper » Processos » NF-e » Importação NF-e

## 3. Escopo

- Atualização automática da aba "ICMS, PIS e COFINS" após confirmação do desmembramento
- Rateio proporcional dos valores de base de cálculo e valor de imposto (ICMS, PIS e COFINS) pelo Valor Total de cada item gerado
- Ajuste de arredondamento: diferença de centavos vai para o item de maior valor; se iguais, para o último da lista
- Garantir integridade ao cancelar o desmembramento (aba permanece intacta com valores originais do XML)

## 4. Criterios de Aceite

### 3.1 — Atualização da Aba de Impostos Pós-Desmembramento
**Dado que** o usuário realize o desmembramento de um item original do XML em dois ou mais produtos distintos,
**Quando** a operação de desmembramento for confirmada,
**Então** o sistema deve recalcular e reconstruir automaticamente os registros na aba "ICMS, PIS e COFINS", substituindo a linha do item original pelas novas linhas dos produtos gerados.

### 3.2 — Regra de Rateio Proporcional pelo Valor Financeiro
**Dado que** o sistema precisa distribuir os valores de base de cálculo e valor do imposto (ICMS, PIS e COFINS),
**Quando** o cálculo for executado,
**Então** aplicar rateio proporcional baseado no Valor Total de cada novo item em relação ao valor total do item original.

- Exemplo: Item original R$ 100,00 | ICMS R$ 18,00 → Item A (R$ 60,00) recebe 60% = R$ 10,80 | Item B (R$ 40,00) recebe 40% = R$ 7,20

### 3.3 — Ajuste de Arredondamento e Totalizadores
**Dado que** a divisão proporcional pode gerar frações de centavos,
**Quando** o somatório não atingir o valor exato do item original,
**Então** aplicar a diferença no item de maior valor financeiro; se iguais, no último item da lista.

## 5. Definicao de Pronto

- [ ] Código revisado
- [ ] Testes manuais realizados
- [ ] PR aprovado

## 6. Informações para Testes

- **Cenário Principal (Sucesso):** Desmembrar item em dois produtos com valores diferentes. Validar aba "ICMS, PIS e COFINS": item pai removido, itens filhos inseridos, valores recalculados proporcionalmente.
- **Cenário Alternativo (Arredondamento):** Desmembrar item com ICMS de R$ 10,00 em 3 produtos iguais. Esperado: R$ 3,33 / R$ 3,33 / R$ 3,34, somando R$ 10,00.
- **Cenário de Exceção:** Cancelar o desmembramento antes de salvar. Validar que a aba permanece intacta.
- **Impactos Colaterais:**
  - Após salvar a importação com desmembramento corrigido, validar que a posterior NF de Entrada na retaguarda grava os dados fiscais individualizados por produto corretamente.
  - Validar se a NF de entrada gravada foi recalculada (ou não) conforme marcado na rotina de importação de XML.

## 7. Resultado Esperado

A aba "ICMS, PIS e COFINS" deve refletir com precisão os itens gerados pelo desmembramento, com os valores de imposto rateados proporcionalmente ao valor financeiro de cada item, garantindo que o somatório seja exatamente igual ao valor original do XML.
