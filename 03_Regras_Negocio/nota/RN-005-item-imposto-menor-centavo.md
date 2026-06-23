---
id: RN-005
titulo: "Itens com imposto calculado inferior a R$ 0,01 não são incluídos na nota gerada"
tipo: regra-negocio
modulo: "fiscal"
status: ativo
criticidade: media
imutavel: true
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - fiscal
  - ibs
  - cbs
  - arredondamento
  - reforma-tributaria
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-05-21"
---

# Itens com imposto calculado inferior a R$ 0,01 não são incluídos na nota gerada

## 1. Definição

Após o rateio proporcional, qualquer item da nota de origem cujo valor de imposto calculado (IBS ou CBS) resulte em valor inferior a R$ 0,01 (um centavo) não deve ser referenciado na nota de crédito/débito gerada.

## 2. Contexto

O sistema monetário brasileiro não opera com frações de centavo. Incluir itens com imposto calculado abaixo de R$ 0,01 geraria itens com valor zero ou inválido na NF-e, causando rejeição na Sefaz ou inconsistência contábil.

## 3. Condição (Se / Então)

- **Se:** após o rateio proporcional ([[RN-004-rateio-proporcional-itens]]), o valor de IBS ou CBS calculado para um item for inferior a R$ 0,01.
- **Então:** esse item não deve ser incluído como linha na nota de crédito/débito gerada.
- **Senão:** o item é incluído normalmente com seus valores rateados.

## 4. Exemplos

### Válido
Nota com 3 itens. Após rateio:
- Item A: IBS = R$ 0,05 → incluído
- Item B: IBS = R$ 0,03 → incluído
- Item C: IBS = R$ 0,004 → **não incluído**

### Inválido
Incluir o Item C com valor R$ 0,004 arredondado para R$ 0,00 ou R$ 0,01 — ambos os comportamentos são incorretos.

## 5. Exceções

Nenhuma exceção prevista pois decorre de limitação do sistema monetário e da Sefaz.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — regra de negócio fixa.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) (critério 3.6) |