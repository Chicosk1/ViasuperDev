---
id: AG-{{id}}
titulo: "{{titulo_da_atividade}}"
tipo: ag
modulo: "{{modulo}}"
status: backlog
prioridade: alta
versao_template: "1.0"
contexto_llm: alto
tags:
  - ag
  - "{{modulo}}"
processos_impactados: []
rns_impactadas: []
jira: ""
responsavel: ""
solicitante: ""
sprint: ""
data_criacao: "{{date:YYYY-MM-DD}}"
data_limite: "{{date:YYYY-MM-DD}}"
data_inicio: ""
data_conclusao: ""
---

# {{titulo_da_atividade}}

## 1. Contexto

Descreva o cenário atual — o que existe hoje e qual o problema ou necessidade
que gerou esta atividade. Seja específico: mencione nomes de rotinas, telas,
tabelas ou parâmetros envolvidos.

## 2. Objetivo

Uma frase. O que deve ser verdade quando esta AG estiver concluída.

## 3. Escopo

### Inclui
- O que deve ser feito nesta AG.

### Não inclui
- O que está fora do escopo e não deve ser tocado.

## 4. Critérios de Aceite

Condições funcionais verificáveis que definem "entregue":
- [ ] Critério 1 — deve ser testável
- [ ] Critério 2 — deve ser testável
- [ ] Critério 3 — deve ser testável

## 5. Definição de Pronto

Condições técnicas que o Claude Code deve verificar antes de commitar:
- [ ] Todos os testes automatizados passando
- [ ] Sem erros de compilação
- [ ] Sem TODOs ou FIXMEs introduzidos
- [ ] Padrão técnico do módulo seguido ([[PT-001-nome]])

## 6. Referências Técnicas

Links para os documentos do vault que o Claude deve consultar:
- [[PROC-001-nome]] — processo principal impactado
- [[RN-001-nome]] — regra de negócio relevante
- [[ARQ-001-nome]] — decisão arquitetural relacionada
- [[PT-001-nome]] — padrão técnico a seguir

## 7. Resultado Esperado

Descreva o artefato de saída: um novo método, uma correção em uma unit
existente, uma nova tabela, uma alteração em parâmetro. Quanto mais
específico, mais preciso o código gerado.