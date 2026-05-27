---
id: PT-001
titulo: "Uso de QueryPegaData e QueryPegaCampo"
tipo: padrao-tecnico
modulo: "global"
linguagem: "delphi"
status: ativo
versao_template: "1.0"
contexto_llm: medio
tags:
  - padrao-tecnico
  - delphi
  - global
  - querypegadata
  - querypegacampo
  - dados
processos_relacionados:
  - PROC-001
data_criacao: "2026-05-21"
data_revisao: "2026-05-21"
---

# Uso de QueryPegaData e QueryPegaCampo

## 1. Objetivo

Definir quando e como usar `QueryPegaData` e `QueryPegaCampo` para executar consultas nomeadas ao servidor de aplicação, garantindo passagem correta de parâmetros, tipos e tamanhos.

## 2. Padrão Definido

| Função | Retorno | Quando usar |
|---|---|---|
| `QueryPegaData` | `OleVariant` contendo os dados de um CDS completo | Preencher um `TVsClientDataSet` com múltiplos registros/colunas |
| `QueryPegaCampo` | `OleVariant` com o valor de um único campo | Obter um valor escalar (ex: um ID, um total, um flag) |

### 2.1 QueryPegaData — preencher um CDS

```pascal
cdsGeraNotaCredDeb.Data := DmConexao.QueryPegaData(
  'VSCONSULTA',                        // nome da query nomeada (VsConsulta)
  '*',                                 // campos: '*' retorna todos
  ['?',      '1:s',                GetFiltros,           // fragmento SQL dinâmico
   'P', 'DTINIEMI', DataNull(drEmissaoINI.Data),         // parâmetro nomeado
   'P', 'DTFIMEMI', DataNull(drEmissaoFIM.Data),
   'P', 'DTINIBX',  DataNull(drBaixaINI.Data  ),
   'P', 'DTFIMBX',  DataNull(drBaixaFIM.Data )],
  [ftString, ftDate, ftDate, ftDate, ftInteger],         // tipo de cada parâmetro
  [1000,          0,      0,      0,         0]);        // tamanho (0 = não string)
```

### 2.2 QueryPegaCampo — obter valor escalar

```pascal
nTotal := IntOf(DmConexao.QueryPegaCampo(
  'VSCONSULTA', // query nomeada
  'NTOT',       // nome do campo a retornar
  ['P', 'TABELA', 'PCONFIG',
   'P', 'CAMPO',  'SERVORION'],
  [ftString, ftString],
  [15, 10]));
```

### 2.3 Estrutura do array de parâmetros

O array `aOutrosValores` segue o seguinte padrão:

| Marcador | Próximo valor | Significado |
|---|---|---|
| `'?'` | `'N:s'` + valor | Substitui o placeholder `%N:s` na query por um fragmento SQL dinâmico |
| `'P'` | nome + valor | Parâmetro nomeado (`:NOME` na query) |

**OBS:** Sempre optar pelo uso dos parâmetros feitos por bind, dado que são mais performáticos para o plano de explicação do Oracle.

```pascal
// Exemplo com fragmento dinâmico e parâmetros nomeados:
['?',  '1:s',      cFragmentoSQL,   // substitui %1:s na query
 'P',  'DTINI',    DataNull(dInicio),
 'P',  'DTFIM',    DataNull(dFim)]
```

## 3. Anti-padrão (o que NÃO fazer)

**Não passar tipo errado para o parâmetro — o servidor rejeitará ou converterá silenciosamente:**

```pascal
// ERRADO: parâmetro de data passado como ftString
['P', 'DTBAIXA', dBaixa],
[ftString],  // ← ERRADO para datas
[10]

// CERTO: usar ftDate e DataNull para datas
['P', 'DTBAIXA', DataNull(dBaixa)],
[ftDate],
[0]
```

**Não usar `QueryPegaData` para buscar um único valor escalar:**

```pascal
// ERRADO: abre CDS inteiro só para pegar um campo
cds.Data := DmConexao.QueryPegaData('SEL_TOTAL', 'NTOT', [], [], []);
nTotal := cds.FieldByName('NTOT').AsInteger;

// CERTO: usa QueryPegaCampo
nTotal := IntOf(DmConexao.QueryPegaCampo('SEL_TOTAL', 'NTOT', [], [], []));
```

## 4. Quando Aplicar

- `QueryPegaData`: sempre que o resultado for atribuído a `.Data` de um `TVsClientDataSet` para exibição em grid ou processamento de múltiplos registros.
- `QueryPegaCampo`: sempre que o objetivo for um único valor — ID, contagem, flag, descrição — sem necessidade de abrir um CDS.
- Ambos: quando a query está cadastrada na `VsConsulta` (consulta nomeada no servidor). Nunca para SQL montado inteiramente no client.

## 5. Exceções Permitidas

- Overload com `oTdCon: TObject` (quarto parâmetro): aceito quando se trabalha com conexão alternativa. Comportamento idêntico ao padrão, o parâmetro extra é ignorado na implementação atual.

## 6. Processos que Usam Este Padrão

- [[PROC-001-gerar-notas-credito-debito-massa]]