---
id: RN-{{id}}
titulo: "{{titulo_da_regra}}"
tipo: regra-negocio
modulo: "{{modulo}}"
status: ativo
criticidade: alta
imutavel: true
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - "{{modulo}}"
processos_relacionados: []
padroes_relacionados: []
data_criacao: "{{date:YYYY-MM-DD}}"
data_revisao: "{{date:YYYY-MM-DD}}"
---

# {{titulo_da_regra}}

## 1. Definição

Uma frase. Sem ambiguidade. Sem "pode ser" ou "geralmente".

## 2. Contexto

Por que esta regra existe — o problema de negócio ou fiscal que ela resolve.

## 3. Condição (Se / Então)

- **Se:** condição que dispara a regra.  
- **Então:** o que o sistema deve fazer.  
- **Senão:** comportamento quando a condição não é atendida *(se aplicável)*.

## 4. Exemplos

### Válido
Situação concreta onde a regra é satisfeita.

### Inválido
Situação concreta onde a regra é violada e o sistema deve rejeitar.

## 5. Exceções

Situações onde esta regra não se aplica e por quê.  
Se não houver: `Nenhuma exceção prevista.`

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| `NOME_PARAMETRO` | `S` / `N` | O que muda no comportamento |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| {{date:YYYY-MM-DD}} | 1.0 | Criação |