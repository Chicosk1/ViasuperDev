---
id: PROC-{{id}}
titulo: "{{titulo_do_processo}}"
tipo: processo
modulo: "{{modulo}}"
sistema: viasuper
versao_sistema: "{{ex: 2026.1}}"
status: rascunho
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - "{{modulo}}"
  - viasuper
rns_relacionadas: []
arquiteturas_relacionadas: []
padroes_relacionados: []
data_criacao: "{{date:YYYY-MM-DD}}"
data_revisao: "{{date:YYYY-MM-DD}}"
---

# {{titulo_do_processo}}

## 1. Objetivo

Uma frase. O que este processo entrega e qual problema do cliente ele resolve.

## 2. Pré-condições

O que deve ser verdade antes de iniciar:
- Parâmetro `X` configurado com valor `Y`
- Tabela `Z` com saldo disponível
- Integração com `[sistema externo]` ativa

## 3. Regras de Negócio Aplicadas

Lista de referências — os detalhes ficam em `03_Regras_Negocio/`:
- [[RN-001-nome-da-regra]]
- [[RN-002-nome-da-regra]]

## 4. Fluxo do Processo

1. 
2. 
3. 
4. 
5. 

## 5. Componentes Técnicos

**Linguagem / Framework:** Delphi / FireDAC  
**Unit principal:** `uNomeDaUnit.pas`  
**Endpoint (se aplicável):** `POST /api/v1/rota`  
**Tabelas envolvidas:** `TABELA_A`, `TABELA_B`  
**Arquitetura de referência:** [[ARQ-001-nome-da-decisao]]

## 6. Casos de Falha

### [Nome do Erro ou Código]
**Sintoma:** O que o usuário ou o log apresenta.  
**Causa:** Por que acontece.  
**Solução:** O que fazer para resolver.

### [Nome do Erro ou Código]
**Sintoma:**  
**Causa:**  
**Solução:**

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| {{date:YYYY-MM-DD}} | 1.0 | Criação |