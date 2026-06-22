# Modo — Plano de Teste Desenvolvedor

Executado após a confirmação do Checklist de Validação (Passo 3 da Fase 2).
Gera o "Plano de Teste Desenvolvedor" completo para entrega ao Analista de Teste.

---

## Passo 1 — Coletar contexto da implementação

Execute os passos abaixo em silêncio antes de apresentar qualquer coisa ao usuário.

### 1a — Ler documentação da AG e contexto RAG

Leia:
- `VAULT_ROOT/99_AGs/doing/AG-XXXXX-*.md` → extraia: título, escopo, critérios de aceite, rotinas citadas
- `VAULT_ROOT/99_AGs/doing/AG-XXXXX-context.md` → extraia: RNs aplicadas, processos impactados, plano técnico

### 1b — Identificar o que foi alterado no worktree

Obtenha a lista de arquivos modificados e o diff completo em relação à branch principal:

```bash
cd "<worktree_path>"
git diff main...HEAD --name-only --diff-filter=ACMR
git diff main...HEAD --unified=5
```

A partir do diff, extraia:
- Os nomes das procedures/functions criadas ou modificadas
- As telas ou rotinas de negócio que foram alteradas (use os nomes das units/classes para inferir o nome de negócio)
- As entidades de negócio afetadas pelas mudanças

### 1c — Rastrear callers dos métodos alterados

Para cada procedure ou function identificada como modificada no diff, busque quais outras units a chamam no repositório.
Isso garante que telas como UCPedido, que chamam um método de UCNota, sejam incluídas no impacto.

```bash
SOURCE=$(python -c "from viasuperdev import config; print(config.SOURCE_ROOT)")

# Para cada método modificado extraído do diff — repita para cada um
grep -rn "NomeDoMetodoAlterado" "$SOURCE" --include="*.pas" \
  | grep -v "__history" \
  | grep -v "NomeDaUnitOndeOMetodoEstaDefinido" \
  | head -20
```

Para cada caller encontrado:
- Identifique o nome de negócio da tela ou rotina que usa o método alterado
- Adicione essa tela à lista de impacto, mesmo que seu arquivo não conste no diff

### 1d — Buscar rotinas indiretamente impactadas no vault

Para cada tela ou processo identificado nos passos anteriores (incluindo callers), busque documentos relacionados:

```bash
SCRIPTS="$(git rev-parse --show-toplevel)/00_Templates_e_Scripts/_scripts"
cd "$SCRIPTS"

# Para cada rotina ou entidade de negócio afetada (incluindo as encontradas via grep)
python -m viasuperdev.indexer --query "<nome da rotina ou entidade>" --k 5

# Análise de impacto cruzado no vault
python "$SCRIPTS/viasuperdev/vault_search.py" --impact AG-XXXXX
```

---

## Passo 2 — Gerar os cenários de teste

### Regras de escrita (OBRIGATÓRIO — sem exceções)

- **Sem linguagem técnica:** não cite nomes de procedures, funções, variáveis, queries SQL, units ou estruturas de código.
- **Perspectiva do usuário final:** descreva o que o analista deve fazer na interface do sistema e o que deve observar como resultado.
- **Nome de negócio para telas e rotinas:** use o nome pelo qual o usuário conhece a tela (ex: "tela de Emissão de Notas", não "uGeraNotaCred").
- **Cobrir callers identificados:** se UCPedido chama um método alterado de UCNota, inclua cenários para a tela de Pedido também.
- **Cobrir regressão:** inclua ao menos um cenário para cada funcionalidade relacionada que NÃO foi alterada mas pode ter sido afetada indiretamente.
- **Um item = um comportamento testável:** cada tópico descreve uma ação específica e seu resultado esperado observável.
- **Completude:** todos os critérios de aceite da AG devem estar cobertos por ao menos um cenário.

### Estrutura dos itens

Para cenários do fluxo principal:
> Em [nome da tela/rotina], [ação que o analista deve executar], verificar que [resultado esperado visível ao usuário].

Para validações de dados:
> Verificar que [entidade de negócio] apresenta [valor ou comportamento esperado] após [ação realizada].

Para cenários de regressão (incluindo telas que chamam métodos alterados):
> Verificar que [comportamento ou funcionalidade existente em nome-da-tela] continua funcionando corretamente e não foi afetado pela alteração.

Para cenários de erro/validação:
> Ao tentar [ação inválida ou fora do esperado], verificar que o sistema [apresenta mensagem / bloqueia / redireciona] adequadamente.

---

## Passo 3 — Apresentar o Plano de Teste Desenvolvedor

Exiba no chat o documento completo no formato abaixo.
Use Markdown com os níveis de cabeçalho exatos indicados.
**Não salve automaticamente — aguarde confirmação do usuário.**

---

# Plano de Teste Desenvolvedor

### Checklist Obrigatório Pelo Desenvolvedor

- **Banco de Dados**
  - Validado a atualização do banco de dados do ViasuperTitan e Viasuper Padrão;
  - Validado performance das consultas alteradas em grande volumes de dados;
- **Sistema**
  - Efetuado teste de CRUD das rotinas alteradas;
  - Validado se o comportamento das rotinas alteradas se mantém conforme o solicitado na tarefa garantindo que outros comportamentos não sejam alterados;

### Plano de Teste

- <cenário 1 — fluxo principal da implementação>
- <cenário 2 — variação ou caso específico coberto pela AG>
- <cenário 3 — validação de dado ou estado esperado>
- <cenário N — regressão de tela que chama método alterado>
- <cenário N+1 — regressão de funcionalidade relacionada>

---

Após apresentar, pergunte:
> "Plano de Teste gerado para AG-XXXXX. Deseja ajustar ou acrescentar algum cenário antes de finalizar?"

Se o usuário solicitar ajustes, regenere os cenários afetados e apresente o documento completo novamente.

---

## Passo 4 — Publicar no Jira (apenas se solicitado)

Nunca publique automaticamente. Aguarde solicitação explícita do usuário.

O campo "Plano de Testes" no Jira é `customfield_10049`.

```
Use: editJiraIssue
  issue: AG-XXXXX
  fields: { "customfield_10049": "<conteúdo do plano em texto formatado>" }
```

Após publicar, informe:
> "Plano de Teste publicado no campo 'Plano de Testes' da issue AG-XXXXX no Jira."
