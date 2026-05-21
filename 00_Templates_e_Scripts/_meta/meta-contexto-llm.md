---
id: META-contexto-llm
titulo: "Contrato — campo contexto_llm"
tipo: meta
status: ativo
versao_template: "1.0"
contexto_llm: baixo
tags:
  - meta
  - indexador
data_criacao: "{{date:YYYY-MM-DD}}"
data_revisao: "{{date:YYYY-MM-DD}}"
---

# Contrato — campo `contexto_llm`

<!--
  contexto_llm: baixo = este próprio arquivo não é vetorizado.
  É documentação de operação do indexador, não conhecimento do domínio.
-->

O campo `contexto_llm` em cada frontmatter instrui o `indexer.py` sobre como
tratar o arquivo durante a vetorização no ChromaDB.

## Valores e comportamento

| Valor | Indexar? | Incluir no contexto do agente por padrão? | Uso típico |
|---|---|---|---|
| `alto` | Sim | Sim | AGs, Processos, Arquiteturas, RNs, Glossários |
| `medio` | Sim | Não (somente via query explícita) | Padrões Técnicos |
| `baixo` | Não | Não | Índices, arquivos de navegação, este arquivo |

## Regra de exclusão no indexer.py

```python
EXCLUDE_CONTEXTO = {"baixo"}

def deve_indexar(frontmatter: dict) -> bool:
    return frontmatter.get("contexto_llm", "alto") not in EXCLUDE_CONTEXTO
```

## Regra de inclusão no contexto do agente

```python
CONTEXTO_DIRETO = {"alto"}

def incluir_no_contexto(frontmatter: dict) -> bool:
    return frontmatter.get("contexto_llm", "alto") in CONTEXTO_DIRETO
```