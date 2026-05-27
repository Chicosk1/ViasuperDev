# Fase 2 — Implementacao no Worktree

As Fases 2 e 3 sao executadas em conjunto: implementacao, revisao e abertura do PR
na mesma sessao.

---

## Passo 0 — Reposicionamento e leitura de estado

Leia `.claude/viasuperdev/AG-XXXXX/branch-state.json`.
Leia o contexto RAG em `VAULT_ROOT/99_AGs/doing/AG-XXXXX-context.md`.

Se o context.md nao existir, volte para a Fase 1.

---

## Passo 1 — Criar worktree para a AG

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --worktree AG-XXXXX
```

O script:
1. Cria branch `feature/AG-XXXXX` a partir de `main` (ou `bugfix/AG-XXXXX` para bugs)
2. Cria worktree em `<SOURCE_ROOT>/../worktrees/AG-XXXXX`
3. Retorna JSON com `worktree_path` e `branch`

Atualize `branch-state.json`:
```json
{"worktree_criado": true, "worktree_path": "<path retornado>"}
```

Informe ao usuario: "Worktree criado em `<path>` na branch `<branch>`."

---

## Passo 2a — Implementacao Autonoma

**Antes de qualquer escrita de codigo:**
1. Consulte todos os padroes tecnicos indexados no vault:
```bash
SCRIPTS="$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"
cd "$SCRIPTS"

# Busca todos os padroes tecnicos disponíveis
python -m viasuperdev.indexer --query "padrao tecnico Delphi Viasuper" --k 10

# Busca especifica pelo tipo de artefato da AG (ex: QueryPegaData, RespOk, TFFormProc)
python -m viasuperdev.indexer --query "<tipo de artefato da AG>" --k 5
```
 
Se a busca semantica retornar score < 0.75 para algum padrao relevante, complemente com busca direta:
```bash
python "$SCRIPTS/vault_search.py" --id PT-001
python "$SCRIPTS/vault_search.py" --id PT-002
# repita para cada PT-XXX listado em `04_Padroes_Tecnicos/`
```
 
Para listar todos os padroes tecnicos disponiveis no vault:
```bash
python "$SCRIPTS/vault_search.py" --list
```
 
Aplique **todos** os padroes tecnicos encontrados.

2. Confirme o tipo de tela com base no Plano Tecnico do context.md

**Fluxo:**

1. Se a tarefa tiver 3 ou mais alteracoes distintas, liste-as via `TodoWrite` antes de iniciar.
   Marque cada item como concluido imediatamente apos executa-lo.

2. **Gere o codigo e exiba no chat para revisao antes de salvar no worktree.**

   Para cada artefato:
   ```
   === <NomeDaUnit>.pas ===
   <codigo completo>
   ===
   ```

   Aguarde confirmacao do usuario antes de salvar no worktree:
   > "Codigo gerado. Revise e confirme para salvar em `<worktree_path>`."

3. Apos confirmacao, salve os arquivos diretamente no worktree:
   ```bash
   # Salva com encoding Windows-1252
   python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" \
     --save-file "<worktree_path>/App/Mercado/<NomeDaUnit>.pas" \
     --encoding windows-1252
   ```

4. Se o usuario solicitar ajustes, regere o trecho afetado, exiba no chat e aguarde nova confirmacao.

**Excecoes — quando NAO implementar autonomamente:**
- Ajustes visuais que exigem posicionamento de componentes no IDE
- Criacao de `.dfm` do zero — o usuario cria o esqueleto, a skill preenche a logica

---

## Passo 2b — Revisao de Codigo

Apos confirmacao da implementacao, antes de qualquer outra acao:

Revise todos os arquivos `.pas` criados/alterados verificando:
- Formatacao de `begin/end` subordinado
- Ausencia de comentarios (exceto referencia AG se solicitada)
- Ausencia de `print()`, `writeln()`, `showmessage()` de debug
- Encoding Windows-1252 nos arquivos `.pas`

Apresente ao usuario um resumo dos pontos verificados e eventuais correcoes aplicadas.
Aguarde confirmacao antes de prosseguir para o Passo 3.

---

## Passo 3 — Checklist de Validacao

```
Checklist — AG-XXXXX
────────────────────────────────────────────
[ ] Sem TODOs ou FIXMEs introduzidos
[ ] Sem comentarios adicionados
[ ] Encoding Windows-1252 confirmado
[ ] Criterios de aceite cobertos: X/Y
[ ] Gaps sinalizados: <lista ou "nenhum">

Para validar no Delphi (usuario):
[ ] Sem erros de compilacao
[ ] Testes manuais conforme criterios de aceite
```

---

## Passo 4 — Mensagem de commit e PR

**Mensagem de commit sugerida** (exibir no chat, nao executar):

```
AG-XXXXX: <verbo no imperativo> <descricao concisa>

- <item 1 implementado>
- <item 2 implementado>

Criterios cobertos: X.X, X.X, X.X
```

**Link do PR** — gerar via script:

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" \
  --pr-url AG-XXXXX
```

Interprete o retorno:
- `status: OK` → exiba o campo `url` ao usuario.
- `status: ERRO` → branch ainda nao registrada; verifique se o Passo 1 foi executado.

Apresente ao usuario:
1. A mensagem de commit sugerida
2. A URL do PR retornada pelo script

> Commit e push continuam sendo feitos pelo usuario. A skill nunca executa `git commit` ou `git push` no worktree.

**Aguarde confirmacao do usuario de que o PR foi aberto antes de prosseguir.**

---

## Encerramento da Fase 2

So encerre apos o usuario confirmar que o PR foi aberto.

Atualize `branch-state.json`:
```json
{"fase_atual": 3, "etapa_atual": "concluido"}
```

Mova a AG para `done/` se o usuario confirmar:
```bash
python -c "
from viasuperdev import config
import shutil, glob

ag_key = 'AG-XXXXX'
matches = glob.glob(str(config.VAULT_ROOT / '99_AGs' / 'doing' / f'{ag_key}*.md'))
matches = [m for m in matches if 'context' not in m and 'rascunho' not in m]
if matches:
    dst = config.VAULT_ROOT / '99_AGs' / 'done'
    dst.mkdir(exist_ok=True)
    shutil.move(matches[0], dst)
    print('AG movida para done/')
"
```

Sugira: "Use `/compact` ou `/clear`. Depois chame `/viasuperdev AG-XXXXX` para retomar se necessario."