# Contexto do Projeto ViasuperDev

## 1. Objetivo do Projeto

Construir um ecossistema de desenvolvimento autônomo que une:
- **Obsidian** como base de conhecimento (KB) local em Markdown
- **ChromaDB** como vector store local persistente
- **HuggingFace** (`intfloat/multilingual-e5-small`) como modelo de embeddings local e gratuito
- **Claude Code** como agente de desenvolvimento ponta a ponta

O pipeline completo: `AG (tarefa) → recuperação de contexto RAG → código → testes → commit`

---

## 2. Sobre o Desenvolvedor

- **Nome:** Gabriel Cichocki
- **Empresa:** Nimitz
- **Produto:** ERP Viasuper (Delphi / Oracle)
- **Stack principal:** Delphi, Oracle, Pascal
- **Jira:** https://nimitz.atlassian.net
- **Vault:** `C:/Repositorios/ClaudeCopilot/ViasuperDev/`
- **OS:** Windows 11, terminal Git Bash no VS Code

---

## 3. Estrutura do Vault

```
VIASUPERDEV/
├── 00_Templates_e_Scripts/
│   ├── _scripts/              ← projeto Python de automação (ver seção 4)
│   └── _templates/            ← templates Obsidian/Templater v1.0
│       ├── Template_AG.md
│       ├── Template_Arquitetura.md
│       ├── Template_Glossario.md
│       ├── Template_Indice.md
│       ├── Template_Padrao_Tecnico.md
│       ├── Template_Processo.md
│       ├── Template_Regra_Negocio.md
├── 01_Indices/                ← flat, sem subpastas por módulo
│   └── IDX-nota.md
├── 02_Processos/
│   └── nota/
│       └── PROC-001-gerar-notas-credito-debito-massa.md
├── 03_Regras_Negocio/
│   └── nota/
│       ├── RN-001-filtro-data-obrigatorio.md
│       ├── RN-002-duplicatas-elegiveis.md
│       ├── RN-003-calculo-base-ajuste-ibs-cbs.md
│       ├── RN-004-rateio-proporcional-itens.md
│       ├── RN-005-item-imposto-menor-centavo.md
│       └── RN-006-configuracao-documento-finalidade.md
├── 04_Padroes_Tecnicos/
│   ├── backend/
│   │   ├── PT-001-uso-querypegadata-querypegacampo.md
│   │   └── PT-002-uso-familia-respok.md
│   ├── frontend/
├── 05_Arquiteturas/           ← atua também como ADR (Architecture Decision Records)
│   └── infra/
│   ├── database/              ← movido de 04_Padroes_Tecnicos
│   └── nota/
│       └── ARQ-001-unit-gera-nota-cred-deb-tela-filtros.md
├── 06_Glossarios/
│   └── GLOS-nota.md           ← 26 termos de reforma tributária e fiscal
└── 99_AGs/
    ├── backlog/
    │   ├── AG-31945-gerar-notas-credito-debito-parte-1.md
    │   └── AG-32021-gerar-notas-credito-debito-parte-2.md
    ├── doing/
    └── done/
```

**Regras de pasta:**
- `01_Indices/` é **flat** — índices são rasos por natureza
- `02_Processos/`, `03_Regras_Negocio/`, `05_Arquiteturas/`, `06_Glossarios/` usam **subpastas por módulo**
- `04_Padroes_Tecnicos/` usa subpastas por **linguagem/stack** (frontend, backend)
- `_scripts/` e `_templates/` são **excluídos da indexação** via configuração do indexer (não são conhecimento, são ferramentas)
- `05_Arquiteturas/` absorve o papel de ADR (Decisões de Arquitetura)

---

## 4. Scripts de Automação

### 4.1 Projeto Python — `_scripts/`

```
_scripts/
├── .env                        ← credenciais (nunca commitar)
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
├── requirements.txt            ← lock file gerado por pip-compile (NÃO editar à mão)
├── requirements-dev.txt        ← ferramentas de dev (-r requirements.txt + pytest/ruff/mypy)
├── README.md
├── jira-to-vault.sh            ← comando principal (workaround Git Bash)
├── templates/
│   ├── ag.j2
│   └── processo.j2
├── tests/
│   ├── test_parsers.py
│   ├── test_vault_writer.py
│   ├── test_jira_client.py
│   ├── test_logging_config.py
│   └── test_indexer.py
└── viasuperdev/
    ├── __init__.py
    ├── cli.py
    ├── config.py
    ├── jira_client.py
    ├── logging_config.py
    ├── parsers.py
    ├── vault_writer.py
    ├── indexer.py              ← Fase 3 — ✅ CONCLUÍDO (KB + source)
    └── run_ag.py               ← Fase 5 — a implementar (não existe ainda)
```

### 4.2 Comando principal (Fase 1)

```bash
bash jira-to-vault.sh AG-XXXXX                                      # Gera AG
bash jira-to-vault.sh AG-XXXXX --tipo processo                      # Gera processo
bash jira-to-vault.sh AG-XXXXX --tipo processo --atualiza PROC-001  # Merge
bash jira-to-vault.sh AG-XXXXX --dry-run                            # Visualiza sem salvar
```

### 4.3 Comandos de indexação (Fase 3 — implementados)

```bash
make index                                                # Indexa vault no ChromaDB (camada KB)
make query Q="base IBS ajustar"                           # Busca semântica — retorna chunks mais similares

python -m viasuperdev.indexer --only kb                   # só camada Markdown
python -m viasuperdev.indexer --full                      # re-indexa tudo (ignora manifesto)
python -m viasuperdev.indexer --query "base IBS ajustar"  # teste RAG
python -m viasuperdev.indexer --stats                     # exibe estatísticas da coleção
python -m viasuperdev.indexer --dry-run                   # simula sem gravar no ChromaDB
```

### 4.4 Comandos planejados (Fase 5)

```bash
make run-ag AG=AG-31945                              # Executa AG via agente (Fase 5)

python -m viasuperdev.indexer --only source          # camada Delphi (Fase 3b)
python -m viasuperdev.run_ag --ag AG-31945 --dry-run # teste contexto
```

### 4.5 Workaround Git Bash

O comando `python -m viasuperdev.cli` não passa argumentos corretamente no
Git Bash do Windows. A solução é o `jira-to-vault.sh` que usa `sys.argv`
diretamente. **Nunca usar `-m viasuperdev.cli` com argumentos no Git Bash.**

### 4.6 Responsabilidades dos módulos

| Módulo | Responsabilidade |
|---|---|
| `config.py` | Única fonte de verdade — paths, thresholds, mapeamentos |
| `logging_config.py` | Inicializa logging — importar antes de tudo no entry point |
| `jira_client.py` | HTTP + auth Jira, dataclass `JiraIssue`, exceções tipadas |
| `parsers.py` | ADF → texto, extração de campos, `parse_ag`, `parse_processo` |
| `vault_writer.py` | Render Jinja2, `slugify`, `next_id`, `write_*`, `merge_processo` |
| `cli.py` | Orquestra os módulos, argparse, entry point |
| `indexer.py` | `MarkdownChunker`, `DelphiMethodChunker`, `HuggingFaceEmbedder`, ChromaDB KB+source, incremental MD5, CLI |
| `run_ag.py` | Orquestrador RAG → contexto → Claude Code CLI — **a implementar** |

---

## 5. Decisões Técnicas Registradas

### 5.1 Stack RAG

| Componente | Decisão | Motivo |
|---|---|---|
| Embeddings | **HuggingFace `intfloat/multilingual-e5-small`** local | Gratuito, sem custo de API, PT-BR nativo, 384d, MIT; Voyage AI descontinuado no projeto |
| Vector store | **ChromaDB** com `PersistentClient` | Local, sem servidor, acesso direto sem LlamaIndex |
| Chunking Markdown | `MarkdownChunker` próprio — split por `##`/`###` | Cada seção = chunk semântico limpo; frontmatter injetado como metadado |
| Chunking Delphi | `DelphiMethodChunker` próprio — regex por `procedure`/`function` | Método = unidade semântica mínima; extrai queries `SEL_*` e tabelas como metadado |
| Coleções ChromaDB | Duas coleções: `knowledge_base` (Markdown) + `source` (Delphi) | Pesos distintos na query: KB=negócio/semântico, source=implementação |
| Indexação | Incremental por hash MD5 + manifesto `.index_manifest.json` | Só re-indexa o que mudou |
| Interface Embedder | Abstrata (`Embedder`) + impl `VoyageEmbedder` | Troca de provider = mudar `EMBEDDINGS_PROVIDER` no `.env` + reindexar |

### 5.2 Arquitetura RAG duas camadas

```
Query do agente
    ↓
ChromaDB "kb"  (peso alto — o que fazer, regras, contexto)
    +
ChromaDB "source" (peso alto — como já foi feito, padrões reais)
    ↓
context_AG-XXXXX.md → Claude Code
```

### 5.3 Contrato do campo `contexto_llm`

| Valor | Indexar? | Incluir no contexto do agente? | Uso típico |
|---|---|---|---|
| `alto` | Sim | Sim | AGs, Processos, Arquiteturas, RNs, Glossários |
| `medio` | Sim | Não (só via query explícita) | Padrões Técnicos |
| `baixo` | **Não** | Não | Índices, _meta, arquivos de navegação |

Documentado em: `00_Templates_e_Scripts/_meta/_meta_contexto_llm.md`

### 5.4 Convenções do vault

- **Sem campo `dominio`** — usar `modulo` (nomenclatura do ERP)
- **`sistema: viasuper`** (não `erp`)
- **Tags em formato lista YAML** (não inline)
- **`05_Arquiteturas/`** atua como ADR — sem pasta separada `07_ADRs/`
- **`99_AGs/`** com subpastas `backlog/doing/done`
- **`arquiteturas_relacionadas`** (não `adrs_relacionados`)
- **`versao_template: "1.0"`** obrigatório em todos os documentos
- **Metadados em português** em todos os frontmatters
- Listas usam `-` (não `*`) nos templates gerados por script

### 5.5 Templates v1.0 — correções aplicadas

Todos os 7 templates foram revisados e corrigidos em relação às versões originais:

| Problema | Correção |
|---|---|
| `status: backlog \| em-progresso` (YAML inválido) | Valor único: `status: backlog` |
| `criticidade: alta \| media \| baixa` (YAML inválido) | Valor único: `criticidade: alta` |
| `data_criacao:\n  "{ date }":`  (chave aninhada) | `data_criacao: "{{date:YYYY-MM-DD}}"` |
| `"{ modulo }":` em tags (dois-pontos) | `- "{{modulo}}"` |
| `versao_template` ausente | Adicionado em todos |
| `linguagem: delphi` hardcoded em PT | `linguagem: "{{linguagem}}"` |
| `adrs_relacionados` em PROC | Renomeado para `arquiteturas_relacionadas` |
| Falta de `definicao_de_pronto` na AG | Adicionado como seção separada dos critérios de aceite |
| Falta de `data_inicio` / `data_conclusao` na AG | Adicionados |
| Falta de `supersedes` / `substituido_por` no ARQ | Adicionados |
| Falta de `criterios_decisao` no ARQ | Adicionado |
| Falta de `total_termos` no GLOS | Adicionado |

### 5.6 Padrões de código Python

- Python 3.11.9
- `pyproject.toml` com `setuptools.build_meta`
- `[tool.setuptools.packages.find] include = ["viasuperdev*"]`
- `logging_config.py` separado — `setup_logging()` é o primeiro call do `main()`
- Sem `basicConfig` fora do `logging_config.py`
- `requirements.txt` é lock file gerado por `pip-compile pyproject.toml` — **não editar à mão**
- Novas dependências de produção → `[project.dependencies]` no `pyproject.toml`, depois `pip-compile`
- Novas dependências de dev → `[project.optional-dependencies] dev` no `pyproject.toml`
- `line-length = 100`, `target-version = "py311"`, ruff rules: `E`, `F`, `I`, `UP`, `B`, `SIM`
- Testes com `pytest`, cobertura com `pytest-cov`

**Dependências adicionadas na Fase 3** (`pyproject.toml`):

```
chromadb
sentence-transformers
python-frontmatter
```

**Variáveis de ambiente adicionadas na Fase 3** (`.env` / `.env.example`):

```
CHROMA_DIR=              # path local do ChromaDB persistente
EMBEDDINGS_PROVIDER=huggingface
EMBEDDINGS_MODEL=intfloat/multilingual-e5-small
SOURCE_ROOT=             # path dos fontes Delphi (usado na Fase 3b)
```

### 5.7 Campos do Jira mapeados

| Campo Jira | Campo no frontmatter | Observação |
|---|---|---|
| `summary` | `titulo` | título da tarefa |
| `assignee.displayName` | `responsavel` | |
| `reporter.displayName` | `solicitante` | |
| `customfield_10150[0].name` | `versao_sistema` | pega só antes do " - " |
| `fixVersions[0].name` | `versao_sistema` | fallback se customfield vazio |
| Breadcrumb ADF (penúltimo `»`) | `modulo` | ex: "» Nota » Nota Fiscal" → "Nota" |
| Último segmento `»` | sugestão `nome_rotina` | prompt no terminal para processos |

### 5.8 Comportamento por tipo de documento

| Tipo | Nome do arquivo | Prompt de nome? | Versão Jira? |
|---|---|---|---|
| `ag` | `AG-XXXXX-titulo-jira.md` | Não — usa título do Jira | Sim |
| `processo` (criar) | `PROC-NNN-nome-rotina.md` | Sim — breadcrumb como sugestão | Sim |
| `processo` (--atualiza) | atualiza existente | Não | Sim |

### 5.9 Versionamento do histórico

- Criação: `1.0`
- Merge via `--atualiza`: incrementa minor automaticamente (`1.0 → 1.1 → 1.2`)
- Coluna: `Mudança` (não `Descrição`)

---

## 6. Documentos Reais no Vault (Fase 2 — Concluída)

Primeiro fluxo completo documentado: **Geração de Notas de Crédito/Débito em Massa**
(AGs AG-31945 e AG-32021, módulo `nota`, reforma tributária IBS/CBS)

| Arquivo | Tipo | Localização |
|---|---|---|
| `PROC-001-gerar-notas-credito-debito-massa.md` | processo | `02_Processos/nota/` |
| `RN-001-filtro-data-obrigatorio.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `RN-002-duplicatas-elegiveis.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `RN-003-calculo-base-ajuste-ibs-cbs.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `RN-004-rateio-proporcional-itens.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `RN-005-item-imposto-menor-centavo.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `RN-006-configuracao-documento-finalidade.md` | regra-negocio | `03_Regras_Negocio/nota/` |
| `ARQ-001-unit-gera-nota-cred-deb-tela-filtros.md` | arquitetura | `05_Arquiteturas/nota/` |
| `PT-001-uso-querypegadata-querypegacampo.md` | padrao-tecnico | `04_Padroes_Tecnicos/backend/` |
| `PT-002-uso-familia-respok.md` | padrao-tecnico | `04_Padroes_Tecnicos/backend/` |
| `AG-31945-gerar-notas-credito-debito-parte-1.md` | ag | `99_AGs/backlog/` |
| `AG-32021-gerar-notas-credito-debito-parte-2.md` | ag | `99_AGs/backlog/` |
| `GLOS-nota.md` | glossario | `06_Glossarios/` |
| `IDX-nota.md` | indice | `01_Indices/` |

**Flags pendentes** (`<!-- ⚠️ VERIFICAR -->`): **zero** — RN-004 resolvida em v1.1 (2026-05-22).

---

## 7. Roadmap de Implementação

```
Fase 1 — Fundação                      ✅ CONCLUÍDA
  ├── 7 templates Markdown v1.0         ✅ (YAML corrigido, metadados PT, campos novos)
  ├── Estrutura de pastas do vault       ✅
  ├── Contrato contexto_llm             ✅ (_meta_contexto_llm_contrato.md)
  └── Scripts Jira → Vault              ✅ (58 testes passando)

Fase 2 — KB seed (documentos reais)    ✅ CONCLUÍDA
  └── 14 documentos reais              ✅ (1 fluxo completo: nota/IBS/CBS)

Fase 3 — indexer.py + ChromaDB (KB)   ✅ CONCLUÍDA
  ├── viasuperdev/indexer.py            ✅
  │   ├── MarkdownChunker               ✅ (split H2/H3, filtro contexto_llm, wikilinks→texto)
  │   ├── HuggingFaceEmbedder           ✅ (multilingual-e5-small, local, gratuito, 384d)
  │   ├── Coleção ChromaDB "knowledge_base" ✅
  │   ├── Indexação incremental MD5     ✅ (manifest_kb.json)
  │   └── CLI completa                  ✅ (--only kb, --query, --stats, --full, --dry-run)
  ├── pyproject.toml atualizado         ✅ (chromadb, sentence-transformers, python-frontmatter)
  ├── requirements.txt regenerado       ✅ (pip-compile)
  ├── make index + make query           ✅ (Makefile)
  └── test_indexer.py                   ✅

Fase 3b — indexer.py camada Source     ✅ CONCLUÍDA
  ├── DelphiMethodChunker               ✅ (split por procedure/function, class function, latin-1)
  ├── Coleção ChromaDB "source"         ✅
  ├── manifest_source.json              ✅
  ├── SOURCE_ROOT via .env              ✅
  ├── --only source | all na CLI        ✅
  └── test_delphi_chunker.py            ✅ (12 testes)

Fase 4 — Pipeline Jira → Vault         ✅ CONCLUÍDA
  ├── jira_client.py                    ✅ (+ customfield_10169 → modulo_jira)
  ├── parsers.py                        ✅ (resolve_modulo: modulo_jira > components > ADF)
  ├── vault_writer.py                   ✅ (+ _reindex_file automático pós-gravação)
  └── cli.py                            ✅

Fase 5 — Skill Claude Code             ✅ CONCLUÍDA
  ├── .claude/skills/viasuperdev.md     ✅ (fluxo 3 fases, busca 3 camadas)
  ├── vault_search.py                   ✅ (fallback camada 2: --id, texto, --section, --impact)
  └── INSTALACAO.md                     ✅

Próximos passos
  ├── Validação em campo da skill       ⏳ (/viasuperdev AG-31945, calibrar threshold 0.75)
  ├── Indexação real do repositório     ⏳ (--only source com SOURCE_ROOT real)
  ├── run_ag.py                         ⏳ (orquestrador RAG — Fase 5 complementar)
  └── make run-ag no Makefile           ⏳
```

---

## 8. Como Retomar Esta Conversa

Cole este arquivo no início de uma nova conversa com o seguinte prompt:

```
Estou retomando o projeto ViasuperDev. Segue o contexto completo:

[conteúdo deste arquivo]

Fases 1 a 5 concluídas. Os próximos passos são:
1. Validação em campo da skill `/viasuperdev` com AGs reais
2. Indexação real do repositório Delphi (`--only source`)
3. Implementação do `run_ag.py` (orquestrador RAG)

Antes de gerar qualquer código novo, leia os arquivos
`viasuperdev/config.py`, `viasuperdev/indexer.py` e
`.claude/skills/viasuperdev.md` para seguir os padrões já estabelecidos.
```

---

## 9. Problemas Conhecidos e Soluções

| Problema | Causa | Solução |
|---|---|---|
| `make` não encontrado | GnuWin32.Make 3.81 não está no PATH | Adicionar `C:/Program Files (x86)/GnuWin32/bin` ao PATH do Git Bash |
| `jira-to-vault` command not found | Entry point não registrado no PATH do Git Bash | Usar `bash jira-to-vault.sh` |
| `-m viasuperdev.cli` não passa argumentos | Bug do Git Bash com `-m` | Usar `jira-to-vault.sh` que usa `sys.argv` diretamente |
| `make test` Error 2 | Make 3.81 não resolve executáveis Python | Usar `python -m pytest` no Makefile |
| Tags com asterisco | Módulo vindo com `**bold**` do ADF | `_strip_md()` aplicado em `resolve_modulo()` |
| Objetivo cortado | Limite de 300 chars insuficiente | Limite aumentado para 600, trunca na última frase |
| `requirements.txt` editado à mão | Deps RAG adicionadas diretamente no lock file | Mover deps para `pyproject.toml`, regenerar com `pip-compile` |
| ChromaDB dimensão incompatível | Troca de provider sem apagar `.chroma/` | Apagar `.chroma/` e rodar `--full` ao trocar `EMBEDDINGS_PROVIDER` |
| `CHROMA_DIR` aponta para path errado | `SOURCE_ROOT` não configurado no `.env` | Definir `CHROMA_DIR` explicitamente no `.env`; confirmar com `python -c "from viasuperdev import config; print(config.CHROMA_DIR)"` |