# viasuper-docs

Base de conhecimento técnico e de negócio do sistema **Viasuper** (ERP), estruturada como um vault [Obsidian](https://obsidian.md) com automação Python para integração com Jira.

---

## O que é este repositório

Um repositório de documentação que serve como *base de conhecimento* para o desenvolvimento do Viasuper. Centraliza regras de negócio, padrões técnicos, decisões arquiteturais, processos e atividades de desenvolvimento (AGs), mantendo rastreabilidade entre código, Jira e documentação.

O conteúdo é consumido diretamente por colaboradores via Obsidian e pelo **Claude Code**, que usa os documentos como contexto para assistência em desenvolvimento Delphi/Oracle.

---

## Estrutura

```
viasuper-docs/
├── 00_Templates_e_Scripts/
│   ├── _scripts/          # Pipeline Python: Jira → Markdown + RAG (ChromaDB)
│   └── _templates/        # Templates markdown para novos documentos
├── 01_Indices/            # Índices de navegação por módulo  (IDX-*)
├── 02_Processos/          # Fluxos de negócio                (PROC-*)
├── 03_Regras_Negocio/     # Regras validáveis pelo sistema   (RN-*)
├── 04_Padroes_Tecnicos/   # Padrões de código Delphi/Oracle  (PT-*)
├── 05_Arquiteturas/       # Decisões arquiteturais           (ARQ-*)
├── 06_Glossarios/         # Vocabulário técnico e fiscal     (GLOS-*)
└── 99_AGs/                # Atividades de Gestão do Jira
    ├── backlog/
    ├── doing/
    └── done/
```

Documentos são organizados por **módulo de negócio** dentro de cada pasta (ex: `03_Regras_Negocio/nota/`).

---

## Tipos de documento

| Prefixo | Tipo | Exemplo | Propósito |
|---------|------|---------|-----------|
| `IDX` | Índice | `IDX-nota.md` | Mapa de navegação de um módulo |
| `PROC` | Processo | `PROC-001-*.md` | Fluxo de negócio completo (pré-condições, componentes, falhas) |
| `RN` | Regra de Negócio | `RN-003-*.md` | Regra se/então com exemplos e exceções |
| `PT` | Padrão Técnico | `PT-001-*.md` | Padrão de código com exemplos e anti-padrões |
| `ARQ` | Arquitetura | `ARQ-001-*.md` | Componentes, tabelas, units e consultas de uma feature |
| `GLOS` | Glossário | `GLOS-nota.md` | Definições de termos do domínio |
| `AG` | Atividade de Gestão | `AG-31945-*.md` | Ticket Jira traduzido para contexto técnico |

---

## Pipeline Jira → Vault

O diretório `00_Templates_e_Scripts/_scripts/` contém um pacote Python (`viasuperdev`) que sincroniza tickets do Jira para documentos Markdown estruturados.

### Setup

```bash
cd 00_Templates_e_Scripts/_scripts
make setup          # cria venv e instala dependências
cp .env.example .env
# edite .env com suas credenciais
```

**Variáveis de ambiente obrigatórias:**

```bash
JIRA_BASE_URL=https://<workspace>.atlassian.net
JIRA_EMAIL=seu.email@empresa.com
JIRA_API_TOKEN=<token>
VAULT_ROOT=<caminho absoluto para este repositório>
```

### Uso

```bash
# Gerar documento de AG a partir de um ticket Jira
jira-to-vault AG-32021

# Gerar documento de Processo
jira-to-vault AG-32021 --tipo processo

# Visualizar sem salvar
jira-to-vault AG-32021 --dry-run

# Buscar e gerar em lote via JQL
jira-to-vault --search 'project = VS AND issuetype = AG AND status = "Em Progresso"'

# Fazer merge em processo existente
jira-to-vault AG-32021 --atualiza PROC-001
```

### Comandos de desenvolvimento

```bash
make test           # roda pytest
make test-cov       # testes com cobertura
make lint           # ruff
make typecheck      # mypy
make check          # lint + typecheck + test (CI)
make format         # formata código

make index          # indexa KB no ChromaDB (RAG)
make index-full     # reindexação completa
make query Q="IBS"  # busca vetorial
```

---

## Integração com Claude Code

A skill `viasuperdev` (em `.claude/skills/viasuperdev/`) instrui o Claude Code a:

- Ler os documentos deste vault como contexto de negócio e técnico
- Seguir os padrões técnicos (`PT-*`) ao sugerir código Delphi/Oracle
- Rastrear AGs e referenciá-las em implementações
- Usar o glossário para vocabulário preciso do domínio fiscal

Para acionar: `/viasuperdev` em qualquer sessão do Claude Code dentro deste repositório.

---

## Contribuindo

1. Use os templates em `00_Templates_e_Scripts/_templates/` para novos documentos.
2. Siga a nomenclatura `PREFIXO-{seq}-{slug}.md` com frontmatter YAML completo.
3. Ao criar uma AG manualmente, prefira o pipeline `jira-to-vault` para manter consistência.
4. Atualize o `IDX-{modulo}.md` do módulo afetado após adicionar documentos.
