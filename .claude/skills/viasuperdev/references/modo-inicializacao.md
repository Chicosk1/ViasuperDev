# Modo de Inicializacao

Auto-acionado na primeira execucao ou quando `--init` e passado.

Informe ao usuario:
> "Bem-vindo ao ViasuperDev! Vou configurar o ambiente — menos de 1 minuto."

---

## Passo -1 — Configurar raiz do projeto

Verifique se a raiz do vault ja esta salva no config pessoal:

```python
import json, pathlib
p = pathlib.Path.home() / '.claude' / 'viasuperdev-config.json'
cfg = json.loads(p.read_text()) if p.exists() else {}
print(cfg.get('vault_root') or 'NAO_CONFIGURADO')
```

- Se retornar um caminho → raiz ja configurada. **Salve como `VAULT` e pule para o Passo 0.**
- Se `NAO_CONFIGURADO` → primeira execucao. Continue:

Detecte a raiz automaticamente via git:

```bash
git -C "$(pwd)" rev-parse --show-toplevel
```

Informe ao desenvolvedor e aguarde confirmacao:
> "Raiz detectada: `<path retornado>`. Este e o caminho correto do repositorio `viasuper-docs`?
> Confirme ou informe o caminho correto."

Apos confirmacao (use o caminho informado ou o detectado), chame:

```bash
python "<vault_root>/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --set-vault "<vault_root>"
```

- `status: OK` → raiz salva. Salve `vault_root` como `VAULT` e prossiga.
- `status: ERRO` → avise o usuario e exiba o `detail`.

> Apos este passo, o caminho fica salvo em `~/.claude/viasuperdev-config.json`
> e nao precisara ser informado novamente.

---

## Passo 0 — Configurar permissoes do Claude Code

```bash
python "$VAULT/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --configure-permissions
```

- `status: OK` → informe quais permissoes foram adicionadas e quais ja estavam presentes.
- `status: ERRO` → avise o usuario e peca verificacao manual de `~/.claude/settings.json`.

> As permissoes (`Read`, `Edit`, `Write`, `Bash`, `Agent`) permitem que a skill trabalhe
> sem interrupcoes. Nenhum commit e feito automaticamente no workspace.

---

## Passo 1 — Verificar e configurar ambiente

```bash
python "$VAULT/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --setup "$VAULT"
```

Leia o JSON retornado e reporte ao usuario. Se qualquer campo iniciar com `ERRO` ou `AUSENTE`, avise.

Campos verificados:
- `vault_root` — caminho do vault Obsidian (do `.env`)
- `chroma_dir` — caminho do ChromaDB (do `.env`)
- `source_root` — repositorio Delphi (do `.env`; opcional — avise se ausente)
- `scripts_ok` — scripts auxiliares presentes
- `index_kb_ok` — coleção `knowledge_base` indexada com chunks
- `index_source_ok` — coleção `source` indexada (opcional)

Se `index_kb_ok: false`:
> "O vault ainda nao esta indexado. Vou indexar agora..."
```bash
cd "$VAULT/00_Templates_e_Scripts/_scripts"
python -m viasuperdev.indexer --only kb
```

Se `index_source_ok: false` e `source_root` configurado:
> "O repositorio Delphi ainda nao esta indexado. Vou indexar agora..."
```bash
python -m viasuperdev.indexer --only source
```

---

## Passo 2 — Criar pasta de estado

```bash
python "$VAULT/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --complete
```

Isso cria `.claude/tasks/` para armazenar os `branch-state.json` por AG
e salva `vault_root` e `scripts_dir` no config pessoal.

---

## Passo 3 — Verificar estado pos-inicializacao

```bash
python "$VAULT/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --check
```

Leia o JSON e **substitua** os valores de `initialized` e `vault_stats` no contexto atual.

Informe ao usuario:
> "ViasuperDev pronto! Configuracoes em `~/.claude/viasuperdev-config.json`."
> - Vault: X documentos indexados
> - ChromaDB: Y chunks na KB, Z chunks no source (ou "source nao configurado")

Prossiga para a tarefa que o usuario queria executar.
