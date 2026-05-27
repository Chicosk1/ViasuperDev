# Modo de Inicializacao

Auto-acionado na primeira execucao ou quando `--init` e passado.

Informe ao usuario:
> "Bem-vindo ao ViasuperDev! Vou configurar o ambiente — menos de 1 minuto."

---

## Passo 0 — Configurar permissoes do Claude Code

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --configure-permissions
```

- `status: OK` → informe quais permissoes foram adicionadas e quais ja estavam presentes.
- `status: ERRO` → avise o usuario e peca verificacao manual de `~/.claude/settings.json`.

> As permissoes (`Read`, `Edit`, `Write`, `Bash`, `Agent`) permitem que a skill trabalhe
> sem interrupcoes. Nenhum commit e feito automaticamente no workspace.

---

## Passo 1 — Verificar e configurar ambiente

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --setup "$(git rev-parse --show-toplevel)"
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
cd "$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"
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
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --complete
```

Isso cria `.claude/viasuperdev/` para armazenar os `branch-state.json` por AG.

---

## Passo 3 — Verificar estado pos-inicializacao

```bash
python "$(git -C "$(pwd)" rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts/viasuperdev/init_viasuperdev.py" --check
```

Leia o JSON e **substitua** os valores de `initialized` e `vault_stats` no contexto atual.

Informe ao usuario:
> "ViasuperDev pronto! Configuracoes em `~/.claude/viasuperdev-config.json`."
> - Vault: X documentos indexados
> - ChromaDB: Y chunks na KB, Z chunks no source (ou "source nao configurado")

Prossiga para a tarefa que o usuario queria executar.