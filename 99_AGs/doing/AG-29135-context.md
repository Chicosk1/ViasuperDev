# Contexto — AG-29135

**AG:** Enviar preços por bandeira para o JETPDV
**Módulo:** pdv | **Jira:** https://nimitz.atlassian.net/browse/AG-29135
**Gaps detectados:** nenhum

---

## Critérios de Aceite

### 4.1 — Enviar Bandeira de Preço no registro da Filial
- **Dado que** possuímos o registro 200 - Lojas
- **Quando** for realizado o envio da carga de Conf. Estabelecimentos para o PDV
- **Então** deverá ser informado o novo campo: Bandeira de Preço

### 4.2 — Exportar preços por Bandeira
- **Dado que** está sendo enviada uma carga de produtos (Seleção, parcial ou total) para o PDV
- **Quando** o envio for processado
- **Então** deverá ser exportado um novo registro (163) separado do estabelecimento:

| Seq | Campo | Tamanho | Decimais | Tipo | Descrição |
|---|---|---|---|---|---|
| 1 | IDBANDEIRA | 10 | 0 | Numérico | Bandeira de preço |
| 2 | ID | 10 | 0 | Numérico | PLU |
| 3 | PRICE | 15 | 3 | Decimal | Preço |
| 4 | START_PRICE | — | — | Data | Início vigência |

- Somente preços de venda normais (ofertas e tabloides continuam no REG12)

---

## Definição de Pronto

- [ ] Campo Bandeira de Preço adicionado ao registro 200 - Lojas
- [ ] Novo registro 163 de preços por bandeira exportado corretamente
- [ ] Carga de seleção, parcial e total validada com preços normais, tabloides e ofertas
- [ ] Tabloides e ofertas continuam no REG12 sem alteração

---

## Modelo de Dados

### Tabela ITEMPRVDA (chave: IDBANDEIRA + IDITEM — SEM ESTAB)
| Campo | Descrição | Uso em REG163 |
|---|---|---|
| `IDBANDEIRA` | Bandeira de preço | → campo 1 (IDBANDEIRA) |
| `IDITEM` | PLU / Código do item | → campo 2 (ID) |
| `PRECO` | Preço de venda atual (on-line) | → PRICE quando sem offline pendente |
| `PRECOOFF` | Preço de venda futuro (off-line) | → PRICE quando > 0 |
| `PRECODTOFF` | Data em que PRECOOFF se torna PRECO | → START_PRICE quando PRECOOFF > 0 |
| `ULTALT` | Data/hora da última alteração de preço | → START_PRICE quando PRECOOFF = 0 |
| `USERALT` | Usuário que alterou | não usado no REG163 |
| `ORIGEMALT` | Origem da alteração | não usado no REG163 |

**Lógica START_PRICE (Ponto 3 confirmado):**
```
PRICE      = CASE WHEN PRECOOFF > 0 THEN PRECOOFF ELSE PRECO END
START_PRICE = CASE WHEN PRECOOFF > 0 THEN PRECODTOFF ELSE ULTALT END
```

### Tabela FILIALCONFCAD
| Campo | Descrição | Uso no REG200 |
|---|---|---|
| `ESTAB` | Estabelecimento | join com FILIAL |
| `IDBANPRECO` | Bandeira de preço do estabelecimento | → IDBANDEIRA no REG200 |

---

## Código Relacionado

### uboActusExpStore.TActusExpStore (REG200)
[score: 0.780 | camada: 2 | fonte: Commons_1/App/JetPDV/bo/uboActusExpStore.pas]

Classe atual — Registro 200 (Stores/Lojas). Serializa em `ToString` com `AddText`.
Não tem campo `BandeiraPreco` ainda.

```pascal
// ToString atual termina com:
AddText(Result, TFuncActus.FormataTexto(Self.Sellen_Token, 60));
// NOVO: adicionar após:
AddText(Result, TFuncActus.FormataInteiro(Self.BandeiraPreco, 10));
```

### uboJetPdvEnvCarga.GeraArquivoConfiguracaoEstabelecimento (linha ~1617)
[score: 0.775 | camada: 2 | fonte: App/Mercado/Viasuper/Server/DM/uboJetPdvEnvCarga.pas]

Loop de preenchimento do `oStore`. Termina com:
```pascal
oStore.NFCeCompactada := cdsDados.AsStr('NFCE_COMPACTADA').Equals('S');
oStore.Pcredsn101 := cdsDados.AsFloat('PCREDNS101');
oStore.PicPay_Token := cdsDados.AsStr('PICPAYTOKEN');
oStore.Sellen_Token := cdsDados.AsStr('PICPAYSELLERTOKEN');
// NOVO: adicionar após Sellen_Token:
oStore.BandeiraPreco := cdsDados.AsInt('IDBANDEIRA');
```

### uboActusExpProdutos.TActusExpProd.SaveToFile (linha ~1361)
[score: 0.779 | camada: 2 | fonte: Commons_1/App/JetPDV/bo/uboActusExpProdutos.pas]

Função `GeraArquivo` interna chama na ordem:
```pascal
GeraArqCabecalho;
GeraArqRegExcluxao;
GeraArqClassMerc; GeraArqForn; GeraArqTpPreco; GeraArqTrib; GeraArqUn; GeraArqMarca;
GeraArqItem; GeraArqKit; GeraArqKitEstab; GeraArqGrupoListBox;
GeraArqTabFin;         // ← REG77 — pós-loop, padrão a seguir
// NOVO: GeraArqPrecosBandeira → logo após GeraArqTabFin
```

### uboActusExpProdutos.TActusExpProd.GeraArqCabecalho (linha ~847)
[score: 0.779 | camada: 2 | fonte: Commons_1/App/JetPDV/bo/uboActusExpProdutos.pas]

Termina com:
```pascal
Arquivo.Add( FlagTipoCarga+'|'+TActusExpProdClassMerc.GetIdRegistro+'|');
// NOVO: adicionar no final:
Arquivo.Add( FlagTipoCarga+'|'+TActusExpProdPrecosBandeira.GetIdRegistro+'|');
```

### uboJetPdvEnvCarga.GeraArquivoProdutos — loop pós-item (linha ~4608)
[score: 0.775 | camada: 2 | fonte: App/Mercado/Viasuper/Server/DM/uboJetPdvEnvCarga.pas]

Após `Gera_Prod_77_TabFin`, adicionar:
```pascal
ObtemDados_Prod_163_PrecosBandeira;
if not cdsDados.IsEmpty then
  Gera_Prod_163_PrecosBandeira;
```

### uboJetPdvEnvCarga.ObtemDados_Prod_77_TabFin (linha 5914) — PADRÃO A REPLICAR
[camada: 2 | fonte: App/Mercado/Viasuper/Server/DM/uboJetPdvEnvCarga.pas]

```pascal
procedure TJetPdvEnvCarga.ObtemDados_Prod_77_TabFin;
begin
  CloseDataSet(cdsDados);
  qrDados.SQL.Text := FdmServer3C.GetSQLByNome('SEL_EXP-ACTUS-REG77');
  if (FFiltroEstab <> '') then
    qrDados.SQL.Text := qrDados.SQL.Text + ' AND (TAB.ESTAB IN ('+FFiltroEstab+')) ';
  cdsDados.Open;
end;
```

---

## Plano Técnico

### Artefatos a modificar

#### 1. `uboActusExpStore.pas` — Commons (`C:\Repositorios\Commons_1\App\JetPDV\bo\`)

**Interface — `TActusExpStore` (private + published):**
```pascal
// private:
FBandeiraPreco: Integer;

// published property:
property BandeiraPreco: Integer read FBandeiraPreco write FBandeiraPreco;
```

**Implementação — `TActusExpStore.ToString` (ao final, após Sellen_Token):**
```pascal
AddText(Result, TFuncActus.FormataInteiro(Self.BandeiraPreco, 10));
```

> ⚠️ **Atenção:** Este arquivo existe em múltiplas cópias do repositório Commons.
> O worktree deve apontar para o repo correto vinculado ao projeto.

---

#### 2. `uboActusExpProdutos.pas` — Commons (`C:\Repositorios\Commons_1\App\JetPDV\bo\`)

**Interface — Novas declarações:**
```pascal
TActusExpProdPrecosBandeira     = class; { Forward }
TActusExpProdPrecosBandeiraList = class(TObjectListActus<TActusExpProdPrecosBandeira>);

// Na TActusExpProd (private):
FListPrecosBandeira: TActusExpProdPrecosBandeiraList;

// Na TActusExpProd (procedure private):
procedure GeraArqPrecosBandeira;

// Na TActusExpProd (published property):
property ListPrecosBandeira: TActusExpProdPrecosBandeiraList
  read FListPrecosBandeira write FListPrecosBandeira;

// Classe item:
TActusExpProdPrecosBandeira = class(TActusExpBaseLine)
private
  FIdBandeira : Integer;
  FIdItem     : String;
  FPreco      : Double;
  FDtInicio   : TDateTime;
public
  constructor Create;
  function ToString: String; override;
  class function GetIdRegistro: String;
published
  property IdBandeira : Integer   read FIdBandeira write FIdBandeira;
  property IdItem     : String    read FIdItem     write FIdItem;
  property Preco      : Double    read FPreco      write FPreco;
  property DtInicio   : TDateTime read FDtInicio   write FDtInicio;
end;
```

**Implementação:**
```pascal
class function TActusExpProdPrecosBandeira.GetIdRegistro: String;
begin
  Result := '163';
end;

function TActusExpProdPrecosBandeira.ToString: String;
begin
  Result := EmptyStr;
  AddText(Result, TFuncActus.FormataBoolean(Self.Excluir));
  AddText(Result, TFuncActus.FormataTexto(Self.IdRegistro, 3));
  AddText(Result, TFuncActus.FormataInteiro(Self.IdBandeira, 10));
  AddText(Result, TFuncActus.FormataTexto(Self.IdItem, 10));
  AddText(Result, TFuncActus.FormataNumero(Self.Preco, 3));
  AddText(Result, TFuncActus.FormataData(Self.DtInicio));
end;

procedure TActusExpProd.GeraArqPrecosBandeira;
var
  oPreco: TActusExpProdPrecosBandeira;
  i: Integer;
begin
  i := 0;
  for oPreco in ListPrecosBandeira do
    begin
    Inc(i);
    if (i = 1) or (i = ListPrecosBandeira.Count) or ((i mod 50) = 0) then
      RetornaCallbackMessage(logrProgress,
        Format('Produtos - Preços por Bandeira (%d/%d)', [ListPrecosBandeira.Count, i]));
    Arquivo.Add(oPreco.ToString);
  end;
end;
```

**Constructor/Destructor em `TActusExpProd`:**
```pascal
// Create: FListPrecosBandeira := TActusExpProdPrecosBandeiraList.Create;
// Destroy: if Assigned(FListPrecosBandeira) then begin FListPrecosBandeira.Clear; FreeAndNil(FListPrecosBandeira); end;
```

**GeraArqCabecalho — ao final:**
```pascal
Arquivo.Add(FlagTipoCarga+'|'+TActusExpProdPrecosBandeira.GetIdRegistro+'|');
```

**SaveToFile.GeraArquivo — após GeraArqTabFin:**
```pascal
GeraArqPrecosBandeira;
```

---

#### 3. `uboJetPdvEnvCarga.pas` — ClaudeCopilot (`App/Mercado/Viasuper/Server/DM/`)

**Declaração (seção `Arquivo de produtos`, após ObtemDados_Prod_150_GrupoListBox):**
```pascal
procedure ObtemDados_Prod_163_PrecosBandeira;
```

**Campo `cdsDados` reutilizado** — sem necessidade de novo CDS (mesmo padrão de REG77).

**Implementação:**
```pascal
procedure TJetPdvEnvCarga.ObtemDados_Prod_163_PrecosBandeira;
begin
  CloseDataSet(cdsDados);
  qrDados.SQL.Text := FdmServer3C.GetSQLByNome('SEL_EXP-ACTUS-REG163');
  if (FTipoCarga = capProdutosParcial) then
    begin
    if (FFiltroEstab <> '') then
      qrDados.SQL.Add(GetSqlUltAlt_ITEM_OR_ITEMESTAB(True))
    else
      qrDados.SQL.Add(GetSqlUltAlt_ITEM);
  end
  else
  if (FTipoCarga = capProdutosSelecao) then
    begin
    qrDados.SQL.Add(FSelecao);
  end;
  cdsDados.Open;
end;
```

**Closure local `Gera_Prod_163_PrecosBandeira` em `GeraArquivoProdutos`:**
```pascal
procedure Gera_Prod_163_PrecosBandeira;
var
  oPreco: TActusExpProdPrecosBandeira;
begin
  oPreco := nil;
  cdsDados.First;
  while not cdsDados.Eof do
    begin
    oPreco := TActusExpProdPrecosBandeira.Create;
    oGerador.ListPrecosBandeira.Add(oPreco);
    oPreco.IdBandeira := cdsDados.AsInt('IDBANDEIRA');
    oPreco.IdItem     := cdsDados.AsStr('ID');
    oPreco.Preco      := cdsDados.AsFloat('PRICE');
    oPreco.DtInicio   := cdsDados.AsDate('START_PRICE');
    cdsDados.Next;
  end;
end;
```

**Chamada em `GeraArquivoProdutos` (após bloco de REG77/TabFin):**
```pascal
oGerador.RetornaCallbackMessage(logrProgress, 'Consultando Preços por Bandeira...');
ObtemDados_Prod_163_PrecosBandeira;
if not cdsDados.IsEmpty then
  begin
  Gera_Prod_163_PrecosBandeira;
  cdsDados.Close;
end;
```

**Adicionar ao `uses` implementation:**
```pascal
// já usa uboActusExpProdutos — nenhuma unit nova necessária
```

---

#### 4. `GeraArquivoConfiguracaoEstabelecimento` — `uboJetPdvEnvCarga.pas`

**No loop de preenchimento de `oStore` (após `Sellen_Token`):**
```pascal
oStore.BandeiraPreco := cdsDados.AsInt('IDBANDEIRA');
```

---

### SQLs a criar/alterar no banco de dados

#### SQL `SEL_EXP-ACTUS-REG200` (alterar)
Adicionar join com FILIALCONFCAD e campo IDBANDEIRA:
```sql
-- Adicionar ao FROM/JOIN existente:
INNER JOIN FILIALCONFCAD FCC ON FCC.ESTAB = F.ESTAB
-- Adicionar ao SELECT:
FCC.IDBANPRECO AS IDBANDEIRA
```
> ⚠️ O SQL está armazenado no banco. Verificar alias atual da tabela FILIAL (provavelmente `F`) e adicionar o join.

#### SQL `SEL_EXP-ACTUS-REG163` (novo)
```sql
SELECT
  I.IDBANDEIRA,
  I.IDITEM AS ID,
  CASE WHEN (I.PRECOOFF > 0 AND I.PRECODTOFF IS NOT NULL)
    THEN I.PRECOOFF
    ELSE I.PRECO
  END AS PRICE,
  CASE WHEN (I.PRECOOFF > 0 AND I.PRECODTOFF IS NOT NULL)
    THEN I.PRECODTOFF
    ELSE I.ULTALT
  END AS START_PRICE
FROM ITEMPRVDA I
WHERE 1=1
-- + filtro de seleção/parcial aplicado via FSelecao/GetSqlUltAlt_ITEM
-- (campo IDITEM deve bater com o filtro de IDITEM do produto exportado)
```

> **Nota:** O filtro de seleção/parcial da carga filtra por IDITEM. O alias do campo no WHERE
> deve ser `I.IDITEM` para compatibilidade com `GetSqlUltAlt_ITEM` e `FSelecao`.

---

### Critérios cobertos
- **4.1**: Campo BandeiraPreco → REG200 → `uboActusExpStore.pas` + SQL REG200 + `uboJetPdvEnvCarga.pas`
- **4.2**: Novo REG163 → `uboActusExpProdutos.pas` + SQL REG163 + `uboJetPdvEnvCarga.pas`
- **2/2 critérios de aceite cobertos**

---

### Riscos / Pontos de Atenção

1. **Commons multi-cópia**: `uboActusExpStore.pas` e `uboActusExpProdutos.pas` existem em `Commons_1`, `Commons_2`, `Commons_3`, `Commons_4` e `Git_1`. A mudança deve ser feita no repositório correto vinculado ao worktree do projeto.
2. **SQL REG200**: Verificar se o SQL existente já possui JOIN com FILIALCONFCAD por outro motivo antes de adicionar novo JOIN.
3. **Filtro REG163 (seleção/parcial)**: O `GetSqlUltAlt_ITEM` filtra por `IDITEM`. Confirmar que o campo correto na tabela/view de REG163 usa o mesmo alias `IDITEM`.
4. **REG163 sem ESTAB**: Confirmado pelo responsável — `ITEMPRVDA` não tem ESTAB na chave, preços são por bandeira+item globalmente.
