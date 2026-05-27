# Modo de Correcao Pos-Reprovacao

Acionado com `--reprovacao` ou automaticamente quando AG esta em `done/` mas o usuario
reporta que foi reprovada.

---

## Passo 1 — Coletar contexto da reprovacao

Leia:
- O frontmatter da AG em `done/` para entender o escopo original
- O `branch-state.json` para saber o worktree e branch usados
- A descricao da reprovacao fornecida pelo usuario (ou do Jira via `jira_client.py`)

Se a descricao da reprovacao nao for clara, acione brainstorm:
> "O motivo de reprovacao nao ficou claro. Vou apresentar o que entendi e precisamos
> alinhar antes de corrigir."

Apresente: o que foi implementado, o que o testador descreveu, e a sua duvida especifica.
Aguarde alinhamento antes de prosseguir.

---

## Passo 2 — Verificar e reativar o worktree

Leia `branch-state.json` para obter `worktree_path` e `branch`.

```bash
# Verifica se o worktree ainda existe
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" \
  --check-worktree AG-XXXXX
```

- `worktree_ok: true` → prossiga diretamente para o Passo 3.
- `worktree_ok: false` → recriar:
  ```bash
  python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" \
    --worktree AG-XXXXX --branch <branch existente>
  ```

Mova a AG de `done/` de volta para `doing/`:
```bash
python -c "
from viasuperdev import config
import shutil, glob

ag_key = 'AG-XXXXX'
matches = glob.glob(str(config.VAULT_ROOT / '99_AGs' / 'done' / f'{ag_key}*.md'))
if matches:
    dst = config.VAULT_ROOT / '99_AGs' / 'doing'
    dst.mkdir(exist_ok=True)
    shutil.move(matches[0], dst)
    print('AG reaberta em doing/')
"
```

---

## Passo 3 — Buscar contexto adicional para a correcao

Execute queries direcionadas ao ponto de reprovacao:
```bash
SCRIPTS="$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"
cd "$SCRIPTS"

# Busca pela regra de negocio que falhou
python -m viasuperdev.indexer --query "<termo do ponto de reprovacao>" --k 3

# Busca no codigo pelo metodo que falhou
python -m viasuperdev.indexer --query "<nome do metodo ou rotina>" --collection source --k 3
```

---

## Passo 4 — Investigar e corrigir no worktree

1. Leia os arquivos relevantes no worktree.
2. Identifique a causa raiz.
3. Gere o codigo corrigido e exiba no chat para revisao.
4. Apos confirmacao, salve no worktree.

---

## Passo 5 — Fechar o ciclo de correcao

Apos confirmacao do usuario:
- Apresente mensagem de commit sugerida no formato padrao
- Apresente link do PR (ou instrua a atualizar o PR existente)
- Mova a AG para `done/` apos confirmacao do usuario

Nao commite nem faca push por conta propria.