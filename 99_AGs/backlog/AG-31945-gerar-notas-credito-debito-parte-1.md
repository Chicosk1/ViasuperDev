---
id: AG-31945
titulo: "Gerar Notas de Crédito e Débito em Massa — Parte 1 de 2 (Filtros e Grid)"
tipo: ag
modulo: "fiscal"
status: em-progresso
prioridade: alta
versao_template: "1.0"
contexto_llm: alto
tags:
  - ag
  - fiscal
  - nfe
  - ibs
  - cbs
processos_impactados:
  - PROC-001
rns_impactadas:
  - RN-001
  - RN-002
  - RN-003
jira: "https://nimitz.atlassian.net/browse/AG-31945"
responsavel: "Oriel Antonio Gaida"
solicitante: ""
sprint: ""
data_criacao: "2026-05-21"
data_limite: ""
data_inicio: ""
data_conclusao: ""
---

# Gerar Notas de Crédito e Débito em Massa — Parte 1 de 2

## 1. Contexto

O sistema já permite emissão de notas de crédito e débito de forma manual desde a AG-30197, mas o processo exige que o usuário crie a nota e calcule os valores de IBS/CBS manualmente. Para empresas com grande volume diário de baixas financeiras (juros, multas, descontos, acréscimos), esse fluxo manual é inviável. Esta AG cria a primeira tela da nova rotina automatizada: filtros de busca e grid de listagem das duplicatas elegíveis.

## 2. Objetivo

Disponibilizar em Viasuper > Processos > Nota a rotina "Gerar Notas de Crédito/Débito" com filtros funcionais e grid de listagem de duplicatas baixadas com valores de ajuste de IBS/CBS preenchidos automaticamente.

## 3. Escopo

### Inclui
- Criação do item de menu em Processos > Nota > Gerar Notas de Crédito/Débito
- Tela com seção de filtros e grid de resultados
- Todos os filtros especificados (Estab, Pessoa, Portador, Emissão, Data de Baixa, Fatura, Duplicata, radio Receber/Pagar)
- Todas as colunas do grid conforme especificação
- Botão Executar com validação de filtro mínimo de data ([[RN-001-filtro-data-obrigatorio]])
- Preenchimento automático das colunas Base IBS à Ajustar e Base CBS à Ajustar ([[RN-003-calculo-base-ajuste-ibs-cbs]])
- Listagem somente de duplicatas com multa, juros, desconto ou acréscimo ([[RN-002-duplicatas-elegiveis]])
- Checkbox Gerar por linha + exibição do botão Próximo ao marcar ao menos um registro
- Edição manual das colunas Base IBS à Ajustar e Base CBS à Ajustar

### Não inclui
- Tela de confirmação e geração das notas (AG-32021)
- Transmissão para Sefaz
- Qualquer alteração em rotinas existentes de nota fiscal

## 4. Critérios de Aceite

- [ ] Menu Processos > Nota exibe o item "Gerar Notas de Crédito/Débito"
- [ ] Ao clicar em Executar sem nenhum filtro de data, o sistema exibe mensagem de validação e não executa a busca
- [ ] Ao filtrar por Data de Baixa ou Data de Emissão, o grid retorna somente duplicatas com ao menos um valor de ajuste (multa, juros, desconto ou acréscimo) > 0
- [ ] Uma duplicata com mais de uma baixa parcial no período aparece como linhas separadas no grid
- [ ] As colunas Base IBS à Ajustar e Base CBS à Ajustar são preenchidas automaticamente com Juros + Multa + Acréscimos − Desconto
- [ ] Os campos Base IBS à Ajustar e Base CBS à Ajustar são editáveis pelo usuário
- [ ] O botão Próximo só aparece após ao menos um checkbox Gerar ser marcado

## 5. Definição de Pronto

- [ ] Todos os testes automatizados passando
- [ ] Sem erros de compilação
- [ ] Sem TODOs ou FIXMEs introduzidos
- [ ] Todos os critérios de aceite validados manualmente conforme seção 6 (Informações para Testes)

## 6. Referências Técnicas

- [[PROC-001-gerar-notas-credito-debito-massa]] — processo completo
- [[RN-001-filtro-data-obrigatorio]] — validação de data obrigatória
- [[RN-002-duplicatas-elegiveis]] — filtro de duplicatas com valores de ajuste
- [[RN-003-calculo-base-ajuste-ibs-cbs]] — fórmula de preenchimento automático
- AG-30197 — implementação original de notas de crédito/débito (referência de regras)

## 7. Resultado Esperado

Nova tela em Processos > Nota com filtros funcionais e grid de duplicatas. Ao executar a busca com filtros válidos, o grid lista as duplicatas elegíveis com todas as colunas especificadas e as bases de ajuste preenchidas automaticamente. O botão Próximo é exibido ao selecionar ao menos um registro via checkbox.

**Informações para testes (da AG original):**
- Acessar a rotina Gerar Notas de Crédito/Débito
- Filtrar duplicatas à receber e à pagar
- Conferir as informações e os registros listados no grid
- Validar se duplicatas com baixas parciais são listadas corretamente
