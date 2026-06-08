# Guia de Uso — ViasuperDev

O **ViasuperDev** e um parceiro de desenvolvimento dentro do Claude Code para auxiliar
no desenvolvimento de AGs no sistema Viasuper/VIASOFT. Ele guia o ciclo completo de uma
tarefa: analise tecnica com RAG semantico e implementacao Delphi em worktree isolado.

> Commit, push e abertura de PR sao sempre responsabilidade do desenvolvedor.

---

## Pre-requisitos

1. **Claude Code** instalado e aberto na pasta raiz do repositorio ViasuperDev
2. **`.env` configurado** com `VAULT_ROOT`, `CHROMA_DIR` e `SOURCE_ROOT`
3. **Vault indexado:** rode `make index` pelo menos uma vez antes de usar a skill

---

## Primeira Vez — Inicializacao

Na primeira chamada, a skill entra automaticamente no **Modo de Inicializacao**:
- Configura permissoes do Claude Code
- Verifica vault e ChromaDB
- Indexa o vault se necessario
- Cria pasta de estado `.claude/tasks/`

Basta chamar normalmente:
```
/viasuperdev AG-XXXXX
```

Para refazer a inicializacao:
```
/viasuperdev --init
```

---

## Como Iniciar uma AG

Abra uma **nova sessao** no Claude Code para cada AG. Isso evita que o contexto
de AGs anteriores interfira.

```
/viasuperdev AG-31945
```

A skill detecta automaticamente a fase pela posicao da AG no vault:

| Localizacao da AG | Fase detectada |
|---|---|
| `99_AGs/backlog/` | Fase 1 nova |
| `99_AGs/doing/` (sem context.md) | Fase 1 em andamento |
| `99_AGs/doing/` (com context.md) | Fase 2 — implementacao |
| `99_AGs/done/` | AG concluida |

---

## As 3 Fases

### Fase 1 — Analise Tecnica e Contexto RAG

**O que acontece:**
1. Pede que voce descreva seu entendimento da tarefa e o fluxo que imagina
2. Le a AG do vault e extrai criterios, RNs, processos e referencias tecnicas
3. Executa busca semantica em 4 camadas: ChromaDB KB → ChromaDB source → vault_search.py → Glob/Grep/Read
4. Monta `AG-XXXXX-context.md` com chunks priorizados e plano tecnico
5. Se houver ambiguidades, aciona brainstorm
6. Exibe link do context.md para sua revisao

**O que voce faz:**
- **Apresentar seu entendimento da tarefa antes da investigacao comecar** (obrigatorio)
- Confirmar (ou nao) a movimentacao da AG para `doing/`
- Participar do brainstorm se necessario
- Revisar o `context.md` gerado
- Confirmar quando pronto para implementar

---

### Fase 2 — Implementacao no Worktree

**O que acontece:**
1. Cria worktree isolado em `<SOURCE_ROOT>/../worktrees/AG-XXXXX` na branch `feature/AG-XXXXX`
2. Gera o codigo Delphi e exibe no chat para revisao (nao salva automaticamente)
3. Apos sua confirmacao, salva os arquivos no worktree
4. Faz revisao de codigo automatica (prefixos, formatacao, ausencia de comentarios)

**O que voce faz:**
- Revisar o codigo gerado antes de confirmar o salvamento
- Testar no Delphi / RAD Studio
- Fazer commit, push e abrir o PR manualmente (a skill nao faz isso)

**Quando a skill NAO implementa autonomamente:**
- Ajustes visuais em `.dfm` que exigem drag-and-drop no IDE
- Qualquer coisa fora do escopo da AG

---

## AG Reprovada

Se uma AG foi reprovada nos testes:
```
/viasuperdev AG-31945 --reprovacao
```

A skill le o contexto da reprovacao, reativa o worktree, busca chunks relevantes para
o ponto de falha e guia a correcao.

---

## Fluxo de Contexto Critico

Em AGs grandes, o Claude Code pode atingir o limite da janela de contexto.

- **Aviso (35% restante):** skill termina a etapa atual e salva rascunho
- **Critico (25% restante):** skill para, salva tudo e avisa:
  > "Contexto critico — rascunho salvo. Use `/compact` ou `/clear` e chame `/viasuperdev AG-XXXXX`."

Ao retomar, a skill le o rascunho e continua de onde parou.

---

## Onde ficam os arquivos

```
VAULT_ROOT/
└── 99_AGs/
    ├── backlog/        ← AGs aguardando
    ├── doing/
    │   ├── AG-XXXXX-titulo.md
    │   ├── AG-XXXXX-context.md    ← Contexto RAG (gerado na Fase 1)
    │   └── AG-XXXXX.rascunho.md  ← Rascunho (se contexto critico)
    └── done/           ← AGs concluidas

SOURCE_ROOT/../worktrees/
└── AG-XXXXX/           ← Worktree isolado da AG

.claude/tasks/
└── AG-XXXXX/
    └── branch-state.json   ← Estado da sessao
```

---

## Atalhos e Parametros

| Comando | O que faz |
|---|---|
| `/viasuperdev AG-XXXXX` | Inicia ou retoma a AG (deteccao automatica de fase) |
| `/viasuperdev AG-XXXXX --reprovacao` | Modo de correcao pos-reprovacao |
| `/viasuperdev --init` | Reexecuta inicializacao do ambiente |
| `/viasuperdev --help` | Exibe este guia |
| `/compact` | Comprime historico (use entre fases) |
| `/clear` | Limpa historico — retome com `/viasuperdev AG-XXXXX` |

---

## Duvidas Frequentes

**Preciso commitar antes de avancar de fase?**
Nao. O commit e feito por voce, quando quiser, apos testar no Delphi.
A skill nunca faz commit ou push no worktree.

**O que e o `/compact`?**
Comprime o historico da conversa para liberar espaco de contexto.
O `branch-state.json` e os arquivos do vault preservam o estado — basta chamar
`/viasuperdev AG-XXXXX` para retomar.

**A skill pode quebrar o codigo?**
Ela gera codigo e exibe no chat para sua revisao antes de qualquer salvamento.
Voce confirma cada artefato antes de ser escrito no worktree.

**O que e o worktree?**
Um checkout isolado do repositorio Delphi em uma pasta separada, na branch da AG.
Voce pode abrir no RAD Studio normalmente. Quando terminar, o worktree pode ser removido
com `init_viasuperdev.py --remove-worktree AG-XXXXX`.