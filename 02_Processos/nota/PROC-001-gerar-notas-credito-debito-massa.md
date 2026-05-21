---
id: PROC-001
titulo: "Geração de Notas de Crédito e Débito em Massa"
tipo: processo
modulo: "nota"
sistema: viasuper
versao_sistema: "2026.1"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - nota
  - nfe
  - ibs
  - cbs
  - reforma-tributaria
  - viasuper
rns_relacionadas:
  - RN-001
  - RN-002
  - RN-003
  - RN-004
  - RN-005
  - RN-006
arquiteturas_relacionadas:
  - ARQ-001
padroes_relacionados: []
jiras_origem:
  - AG-31945
  - AG-32021
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Geração de Notas de Crédito e Débito em Massa

## 1. Objetivo

Permitir que o analista financeiro gere Notas de Crédito e Débito em lote a partir de juros, multas, acréscimos e descontos registrados nas baixas de duplicatas, ajustando proporcionalmente os valores de IBS e CBS das notas fiscais de origem.

## 2. Pré-condições

- Certificado digital válido em Configurações > Gerais > Filial > Configuração NFE
- Ambiente de emissão configurado (Homologação ou Produção)
- DFe devidamente configurado
- Existência de duplicatas (a receber ou a pagar) com baixas que contenham multa, juros, acréscimos ou descontos
- Configuração de documento com finalidade de emissão `5 - Nota de Crédito` ou `6 - Nota de Débito` cadastrada

## 3. Regras de Negócio Aplicadas

- [[RN-001-filtro-data-obrigatorio]] — ao menos um filtro de data deve ser preenchido
- [[RN-002-duplicatas-elegiveis]] — somente duplicatas com multa, juros, desconto ou acréscimo são listadas
- [[RN-003-calculo-base-ajuste-ibs-cbs]] — fórmula de cálculo da Base CBS/IBS a Ajustar
- [[RN-004-rateio-proporcional-itens]] — rateio da base de ajuste pelos itens da nota de origem
- [[RN-005-item-imposto-menor-centavo]] — itens com imposto calculado inferior a R$ 0,01 não são referenciados
- [[RN-006-configuracao-documento-finalidade]] — configuração de documento deve ter finalidade 5 ou 6

## 4. Fluxo do Processo

### Tela 1 — Filtros e listagem

1. Acessar Viasuper > Processos > Nota > Gerar Notas de Crédito/Débito
2. Preencher ao menos um filtro de intervalo de datas (Data de Emissão ou Data de Baixa) — conforme [[RN-001-filtro-data-obrigatorio]]
3. Preencher opcionalmente: Estab, Pessoa, Portador, Fatura, Duplicata
4. Selecionar o tipo: Duplicata a Receber ou Duplicata a Pagar (radio group)
5. Clicar em **Executar**
6. O sistema retorna no grid todas as baixas (totais ou parciais) de duplicatas que possuam multa, juros, desconto ou acréscimo — conforme [[RN-002-duplicatas-elegiveis]]
7. O sistema preenche automaticamente as colunas **Base CBS à Ajustar** e **Base IBS à Ajustar** — conforme [[RN-003-calculo-base-ajuste-ibs-cbs]]
8. O usuário pode editar os campos **Base IBS à Ajustar** e **Base CBS à Ajustar** por linha
9. O usuário marca o checkbox **Gerar** nas linhas que devem originar notas
10. Ao marcar ao menos um checkbox, o botão **Próximo** é exibido

### Tela 2 — Confirmação e geração

11. Clicar em **Próximo** — o sistema carrega nova tela com os registros selecionados
12. Selecionar a **Configuração de Documento** (finalidade 5 ou 6) — obrigatório conforme [[RN-006-configuracao-documento-finalidade]]
13. Clicar em **Gerar Notas**
14. O sistema valida o preenchimento da Configuração de Documento
15. Para cada registro selecionado, o sistema:
    - Recupera os itens da nota fiscal de origem
    - Rateia proporcionalmente a Base IBS/CBS a Ajustar pelos itens — conforme [[RN-004-rateio-proporcional-itens]]
    - Descarta itens com imposto calculado inferior a R$ 0,01 — conforme [[RN-005-item-imposto-menor-centavo]]
    - Gera a nota de crédito/débito com os valores rateados, usando a Pessoa e o Estabelecimento da duplicata/nota de origem
16. Durante a geração, exibe barra de progresso ao usuário
17. Notas geradas ficam disponíveis para transmissão à Sefaz via NF-e

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** Viasuper > Processos > Nota > Gerar Notas de Crédito/Débito
- **Disponibilidade:** Somente Viasuper Padrão
- **Unit principal:** `uGeraNotaCredDeb.pas`
- **Tabelas envolvidas:**
  - `DUPPAG`, `DUPREC` — duplicatas a receber/pagar
  - `DUPPAGACERFIN`, `DUPRECACERFIN`, `ACERDPA`,`ACERDRE`, `` — baixas de duplicatas (multa, juros, desconto, acréscimo)
  - `NOTAITEM`, `NOTAITEMIMPOSTOIVA`, `NOTAACERFIN`, `ACERFIN` — nota de origem e seus itens
  - `NOTACONF` — config. de documento (finalidade 5/6)
  - `PESSOADOC`, `FILIAL`, `PORTADOR` - auxiliares
- **Consultas envolvidas:** 
  - `SEL_MERC_GERANOTACREDDEB_DUPPAG` - duplicata a pagar
  - `SEL_MERC_GERANOTACREDDEB_DUPREC` - duplicata a receber
- **Implementação detalhada:** [[ARQ-001-unit-gera-nota-cred-deb-tela-filtros]]

## 6. Casos de Falha

### Nenhum filtro de data preenchido
- **Sintoma:** Ao clicar em Executar, o sistema exibe mensagem de validação.
- **Causa:** Nenhum intervalo de data (Emissão ou Data de Baixa) foi informado.
- **Solução:** Preencher ao menos um dos filtros de data antes de executar.

### Nenhuma duplicata retornada
- **Sintoma:** Grid vazio após clicar em Executar.
- **Causa:** Nenhuma baixa no período informado possui multa, juros, desconto ou acréscimo, ou os filtros são restritivos demais.
- **Solução:** Revisar os filtros aplicados e verificar se existem baixas com valores de ajuste no período.

### Configuração de documento inválida
- **Sintoma:** Ao clicar em Gerar Notas, o sistema exibe erro de validação.
- **Causa:** Campo Conf. de Documento não preenchido ou preenchido com finalidade diferente de 5 ou 6.
- **Solução:** Selecionar uma configuração de documento com finalidade `5 - Nota de Crédito` ou `6 - Nota de Débito`.

### Nota gerada sem itens
- **Sintoma:** Nota de crédito/débito gerada sem itens ou com itens faltando.
- **Causa:** Todos os itens da nota de origem resultaram em imposto calculado inferior a R$ 0,01 após o rateio.
- **Solução:** Revisar os valores de Base IBS/CBS à Ajustar informados — conforme [[RN-005-item-imposto-menor-centavo]].

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-05-21 | 1.1 | Merge com [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) — Gerar Notas de crédito e débito em massa 2 de 2 |
| 2026-05-21 | 1.0 | Criação a partir de [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) — Gerar Notas de crédito e débito em massa 1 de 2 |
