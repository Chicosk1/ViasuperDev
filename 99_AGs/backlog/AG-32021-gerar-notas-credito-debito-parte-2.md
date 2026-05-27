---
id: AG-32021
titulo: "Gerar Notas de Crédito e Débito em Massa — Parte 2 de 2 (Confirmação e Geração)"
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
  - rateio
processos_impactados:
  - PROC-001
rns_impactadas:
  - RN-004
  - RN-005
  - RN-006
jira: "https://nimitz.atlassian.net/browse/AG-32021"
responsavel: "Gabriel Samudio Cichocki"
solicitante: ""
sprint: ""
data_criacao: "2026-05-21"
data_limite: ""
data_inicio: ""
data_conclusao: ""
---

# Gerar Notas de Crédito e Débito em Massa — Parte 2 de 2

## 1. Contexto

Continuação direta da AG-31945. Com os registros selecionados na tela de filtros, esta AG implementa a segunda tela do fluxo: confirmação dos registros selecionados, configuração do tipo de documento a emitir e geração efetiva das notas com rateio proporcional de IBS/CBS nos itens da nota de origem.

## 2. Objetivo

Gerar as notas de crédito/débito em lote a partir dos registros selecionados na tela anterior, com rateio proporcional correto de IBS e CBS nos itens da nota de origem e barra de progresso durante o processamento.

## 3. Escopo

### Inclui
- Tela 2 com grid de registros selecionados (mesmas colunas da tela 1)
- Campo de seleção de Configuração de Documento (finalidade 5 ou 6 apenas) — [[RN-006-configuracao-documento-finalidade]]
- Botão Gerar Notas com validação de Conf. de Documento obrigatória
- Geração das notas usando: configuração de documento selecionada, pessoa e estabelecimento da duplicata/nota de origem, itens da nota de origem
- Rateio proporcional de Base IBS/CBS a Ajustar pelos itens — [[RN-004-rateio-proporcional-itens]]
- Exclusão de itens com imposto < R$ 0,01 — [[RN-005-item-imposto-menor-centavo]]
- Barra de progresso durante geração em lote
- Disponibilidade somente no Viasuper Padrão

### Não inclui
- Transmissão automática para Sefaz (notas ficam disponíveis para transmissão manual)
- Tela de filtros (AG-31945)
- Alteração em rotinas existentes de nota fiscal

## 4. Critérios de Aceite

- [ ] Ao clicar em Próximo na tela 1, a tela 2 carrega com exatamente os registros marcados via checkbox
- [ ] O campo Conf. de Documento exibe somente configurações com finalidade 5 ou 6
- [ ] Ao clicar em Gerar Notas sem preencher Conf. de Documento, o sistema exibe mensagem de validação e bloqueia
- [ ] Para cada registro selecionado, é gerada uma nota com a Pessoa e Estabelecimento corretos (da duplicata/nota de origem)
- [ ] Os itens da nota gerada refletem o rateio proporcional de Base IBS/CBS à Ajustar pelo valor de cada item em relação ao total da nota de origem
- [ ] Itens com imposto calculado inferior a R$ 0,01 não aparecem na nota gerada
- [ ] Barra de progresso é exibida durante a geração em lote
- [ ] Notas geradas ficam disponíveis para transmissão à Sefaz
- [ ] Rotina disponível apenas no Viasuper Padrão

## 5. Definição de Pronto

- [ ] Todos os testes automatizados passando
- [ ] Sem erros de compilação
- [ ] Sem TODOs ou FIXMEs introduzidos
- [ ] Rateio validado manualmente com ao menos 2 notas de origem (uma com 1 item e outra com 3+ itens)
- [ ] Transmissão de ao menos 1 nota gerada à Sefaz em ambiente de homologação realizada com sucesso

## 6. Referências Técnicas

- [[PROC-001-gerar-notas-credito-debito-massa]] — processo completo
- [[RN-004-rateio-proporcional-itens]] — rateio proporcional de IBS/CBS
- [[RN-005-item-imposto-menor-centavo]] — exclusão de itens com imposto < R$ 0,01
- [[RN-006-configuracao-documento-finalidade]] — validação da configuração de documento
- AG-30197 — regras de notas de crédito/débito que se aplicam ao rateio

<!-- ⚠️ VERIFICAR: confirmar regras adicionais da AG-30197 que se aplicam ao rateio (imagem referenciada na especificação original não está acessível) -->
<!-- ⚠️ VERIFICAR: acessar planilha de exemplo de rateio https://docs.google.com/spreadsheets/d/1VYtVksYsM4kBE8j9m4FHem0TLeY33Uo6xtmGk6dMHvw para validar fórmula exata -->

## 7. Resultado Esperado

Ao clicar em Gerar Notas na tela 2 com registros selecionados e Conf. de Documento preenchida, o sistema gera uma nota de crédito/débito por registro, com itens rateados proporcionalmente, descartando itens com imposto < R$ 0,01, e exibe barra de progresso durante o processamento. As notas ficam disponíveis para transmissão manual à Sefaz.

**Informações para testes (da AG original):**
- Acessar a rotina Gerar Notas de Crédito/Débito
- Filtrar duplicatas à receber e à pagar
- Selecionar duplicatas e clicar no botão Próximo
- Validar os dados exibidos no grid e gerar notas
- Acessar alguma nota gerada e transmitir para a Sefaz
