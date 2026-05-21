---
id: ARQ-{{id}}
titulo: "{{titulo_da_arquitetura}}"
tipo: arquitetura
modulo: "{{modulo}}"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - arquitetura
  - "{{modulo}}"
criterios_decisao:
  - "{{ex: performance}}"
  - "{{ex: compatibilidade com Delphi}}"
processos_relacionados: []
rns_relacionadas: []
substitui: ""
substituido_por: ""
data_criacao: "{{date:YYYY-MM-DD}}"
data_revisao: "{{date:YYYY-MM-DD}}"
---

# {{titulo_da_arquitetura}}

## 1. Objetivo

Uma frase. O problema técnico que esta arquitetura resolve.

## 2. Decisão

O que foi escolhido e por quê. Voz ativa e direta:
"Utilizamos X porque Y. Descartamos Z porque W."

## 3. Componentes

| Componente | Tipo | Responsabilidade |
|---|---|---|
| `uNomeDaUnit.pas` | Unit Delphi | O que ela faz |
| `TABELA_A` | Tabela Oracle | O que ela armazena |
| `POST /api/v1/rota` | Endpoint | O que ele recebe |

## 4. Código de Referência

```pascal
// Trecho central que materializa esta decisão arquitetural.
// Foque no padrão estrutural, não na implementação completa.
```

## 5. Alternativas Descartadas

| Alternativa | Motivo da rejeição |
|---|---|
| Opção A | Por que não foi escolhida |
| Opção B | Por que não foi escolhida |

## 6. Consequências

### Positivas
- O que esta decisão facilita.

### Negativas / Riscos
- O que esta decisão dificulta ou o risco que ela carrega.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| {{date:YYYY-MM-DD}} | 1.0 | Criação |