# Fase 1 — Analise Tecnica e Montagem de Contexto

**Objetivo:** Ler a AG, montar contexto RAG completo a partir do ChromaDB e formular
o plano tecnico. Nada de codigo ainda.

---

## Etapa 0 — Preparacao

**Passo 0a — Inicializar estado da AG:**

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" \
  --init-ag AG-XXXXX
```

O script cria `.claude/viasuperdev/AG-XXXXX/branch-state.json` com todos os campos
inicializados corretamente. Se o arquivo ja existir, retorna o estado atual sem sobrescrever.

Interprete o retorno:
- `status: CRIADO` → arquivo criado, prossiga.
- `status: JA_EXISTE` → sessao anterior detectada. Leia `etapa_atual` e retome de onde parou.
- `status: ERRO` → avise o usuario e exiba o `detail`.

**Passo 0b — Localizar e ler a AG:**

```bash
python -c "
from viasuperdev import config
import glob

ag_key = 'AG-XXXXX'
pattern = str(config.VAULT_ROOT / '99_AGs' / '**' / f'{ag_key}*.md')
matches = [m for m in glob.glob(pattern, recursive=True)
           if 'rascunho' not in m and 'context' not in m]
print(matches[0] if matches else 'NAO_ENCONTRADO')
"
```

Leia o arquivo completo. Extraia e registre:

| Campo | Origem | Uso |
|---|---|---|
| `titulo` | frontmatter | identificacao e seed de busca |
| `modulo` | frontmatter | filtro ChromaDB |
| `processos_impactados` | frontmatter | busca dirigida PROC-XXX |
| `rns_impactadas` | frontmatter | busca dirigida RN-XXX |
| `tags` | frontmatter | seeds adicionais |
| Criterios de Aceite | secao 4 | DoD da implementacao |
| Definicao de Pronto | secao 5 | checklist de saida |
| Referencias Tecnicas | secao 6 | seeds adicionais |
| Resultado Esperado | secao 7 | artefato esperado |

**Passo 0c — Mover AG para doing/ (se necessario):**

Se a AG estiver em `backlog/`, pergunte ao usuario:
> "AG encontrada em `backlog/`. Mover para `doing/` antes de continuar? (s/N)"

Se confirmado:
```bash
python -c "
from viasuperdev import config
import shutil, glob

ag_key = 'AG-XXXXX'
matches = glob.glob(str(config.VAULT_ROOT / '99_AGs' / 'backlog' / f'{ag_key}*.md'))
if matches:
    dst = config.VAULT_ROOT / '99_AGs' / 'doing'
    dst.mkdir(exist_ok=True)
    shutil.move(matches[0], dst)
    print('Movida para doing/')
"
```

---

## Etapa 1 — Investigacao Autonoma (interna, sem interacao)

Execute a investigacao completa **antes de apresentar qualquer coisa ao usuario**.
Chegue com o plano tecnico ja formulado, nao com perguntas.

### Estrategia RAG em 4 camadas

Para cada documento necessario, tente as camadas em ordem.
**Limiar:** score >= 0.75 = resultado util. Abaixo → proxima camada.

**Camada 1 — ChromaDB KB (semantico):**
```bash
SCRIPTS="$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"
cd "$SCRIPTS"

# Query 1: titulo + modulo
python -m viasuperdev.indexer --query "<titulo da AG>" --k 5

# Query 2: cada RN impactada
python -m viasuperdev.indexer --query "<RN-XXX nome da RN>" --k 3

# Query 3: cada processo impactado
python -m viasuperdev.indexer --query "<PROC-XXX nome>" --k 3

# Query 4: termos tecnicos dos criterios de aceite
python -m viasuperdev.indexer --query "<termo tecnico>" --k 3
```

**Camada 2 — ChromaDB source (codigo Delphi):**

Executar apenas se `SOURCE_ROOT` configurado:
```bash
# Busca por nome de rotina/tela
python -m viasuperdev.indexer --query "<nome da tela ou rotina>" --collection source --k 5

# Busca por tipo de tela + modulo
python -m viasuperdev.indexer --query "<modulo> <TFFormProc ou padraoCds>" --collection source --k 3
```

**Camada 3 — vault_search.py (score < 0.75 ou camada 1/2 insuficiente):**
```bash
SCRIPTS="$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"

# Por ID exato — sempre tentar primeiro
python "$SCRIPTS/vault_search.py" --id RN-XXX
python "$SCRIPTS/vault_search.py" --id PROC-XXX

# Por termo livre
python "$SCRIPTS/vault_search.py" "<regra de negocio>"

# Por secao especifica
python "$SCRIPTS/vault_search.py" "<termo>" --section regras-negocio

# Analise de impacto
python "$SCRIPTS/vault_search.py" --impact AG-XXXXX
```

Secoes validas: `definicao`, `contexto`, `regras-negocio`, `exemplos`, `excecoes`,
`parametros`, `historico`, `objetivo`, `escopo`, `criterios`, `dod`, `referencias`, `resultado`

**Camada 4 — Glob + Grep + Read no repositorio (source nao indexado ou lacunas):**

Quando as camadas 1-3 nao cobrirem pontos tecnicos especificos:
```bash
SOURCE=$(python -c "from viasuperdev import config; print(config.SOURCE_ROOT)")

# Localizar units por nome
find "$SOURCE" -name "uGera*.pas" -not -path "*__history*" 2>/dev/null | head -10
find "$SOURCE" -name "*Nota*.pas" -not -path "*__history*" 2>/dev/null | head -10

# Rastrear procedures por nome
grep -rn "procedure.*ValidarFiltros" "$SOURCE" --include="*.pas" 2>/dev/null | head -10
grep -rn "procedure.*CarregarNotaCredDeb" "$SOURCE" --include="*.pas" 2>/dev/null | head -10

# Ler arquivo especifico
cat "$SOURCE/caminho/para/uNomeDaUnit.pas"
```

**Limite de leitura direta:** leia no maximo 10 arquivos `.pas` por sessao.
Se atingir o limite com pontos abertos, salve rascunho e apresente ao usuario:
> "Atingi o limite de leitura (10 arquivos). Pendencias: [lista]. Qual priorizar?"

### Registro de gaps

Para cada documento que nenhuma camada encontrou, registre em `branch-state.json`:
```json
"gaps_contexto": ["RN-XXX nao localizada", "PROC-XXX nao localizada"]
```

Gaps nao bloqueiam — continue com o que tiver e sinalize ao usuario no resumo.

---

## Etapa 2 — Brainstorm (apenas se necessario)

Apresente algo ao usuario somente se houver:
- Regra ambigua ou contraditoria que o vault nao resolve
- Divergencia entre o que a AG pede e o que o codigo existente faz
- Decisao de negocio que nao pode ser inferida

Se nao houver nenhum desses casos, va direto para a geracao do contexto.

Quando houver brainstorm: apresente a solucao ja formulada e aponte o que precisa de validacao.
Nunca faca brainstorm aberto sem ter o plano em maos.

---

## Etapa 3 — Gerar o Contexto RAG

Monte `VAULT_ROOT/99_AGs/doing/AG-XXXXX-context.md`:

```markdown
# Contexto — AG-XXXXX

**AG:** <titulo>
**Modulo:** <modulo> | **Jira:** <url>
**Gaps detectados:** <lista ou "nenhum">

## Criterios de Aceite
<lista completa da AG>

## Definicao de Pronto
<lista completa da AG>

## Regras de Negocio
### <RN-XXX> — <titulo> § <secao>
<texto do chunk>
[score: X.XXX | camada: N | fonte: path_rel]

## Processos
### <PROC-XXX> — <titulo> § <secao>
<texto do chunk>
[score: X.XXX | camada: N | fonte: path_rel]

## Codigo Relacionado
### <unit>.<method> (<modulo>)
<texto do chunk>
[score: X.XXX | camada: N | fonte: path_rel]

## Plano Tecnico
### Artefatos a criar
- <NomeDaUnit>.pas — <tipo de tela e heranca>
- <SEL_CONSTANTE> — consulta Mestre (se aplicavel)

### Artefatos a modificar
- <UnitDeMenu>.pas — adicionar item de menu
- <Projeto>.dpr — registrar nova unit

### Regras aplicadas
- <RN-XXX>: <resumo da regra>

### Criterios cobertos
X/Y criterios de aceite
```

Apresente ao usuario:
```
Contexto montado para AG-XXXXX:
────────────────────────────────────────────
  RNs:          X chunks (camadas usadas: N)
  Processos:    X chunks (camadas usadas: N)
  Codigo:       X chunks (ou "indisponivel")
  Gaps:         <lista ou "nenhum">
  Arquivo:      <path do context.md>
────────────────────────────────────────────
Revise o context.md e confirme para prosseguir para a Fase 2.
```

Apresente o link do arquivo: `[AG-XXXXX-context.md](<path completo>)`
NAO exiba o conteudo no chat.

**Encerramento da Fase 1:**

So avance apos confirmacao explicita do usuario ("revisado", "pode avancar", "fase 2").
Atualize `branch-state.json`:
```json
{"fase_atual": 2, "etapa_atual": "criacao-worktree"}
```
Sugira: "Para continuar, use `/compact` ou `/clear`. Depois chame `/viasuperdev AG-XXXXX`."