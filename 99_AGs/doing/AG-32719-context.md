# Contexto — AG-32719

**AG:** Inconsistência nos impostos ao gravar nota fiscal após desmembramento de produtos na importação de XML
**Módulo:** NF-e / Importação NF-e | **Jira:** https://nimitz.atlassian.net/browse/AG-32719
**Gaps detectados:** RN específica de desmembramento de impostos no XML não existe no vault (RN-004 e RN-005 são para geração de notas de crédito/débito). Unit `udmItemNfe` mencionada pelo desenvolvedor não localizada (possivelmente nome alternativo).

---

## Critérios de Aceite

### 3.1 — Atualização da Aba de Impostos Pós-Desmembramento
**Dado que** o usuário realize o desmembramento de um item original do XML em dois ou mais produtos distintos,
**Quando** a operação de desmembramento for confirmada,
**Então** o sistema deve recalcular e reconstruir automaticamente os registros na aba "ICMS, PIS e COFINS", substituindo a linha do item original pelas novas linhas dos produtos gerados.

### 3.2 — Regra de Rateio Proporcional pelo Valor Financeiro
Aplicar rateio proporcional baseado no **Valor Total** (`VALPRODBRUTO`) de cada novo item gerado em relação ao valor total do item original.
- Exemplo: Item R$ 100,00 | ICMS R$ 18,00 → Item A (60%) = R$ 10,80 | Item B (40%) = R$ 7,20

### 3.3 — Ajuste de Arredondamento e Totalizadores
A diferença de centavos (sobra do arredondamento) deve ser aplicada automaticamente:
- No **item de maior valor financeiro** (`VALPRODBRUTO`) resultante do desmembramento
- Se **valores idênticos**, aplicar no **último item** da lista desmembrada

### 3.4 — Cancelamento (não altera)
Cancelar antes de confirmar → aba de impostos permanece intacta com valores originais do XML.

---

## Definição de Pronto
- [ ] Código revisado
- [ ] Testes manuais realizados (cenário principal, arredondamento, cancelamento, impactos colaterais)
- [ ] PR aprovado

---

## Regras de Negócio

### RN-004 — Rateio proporcional de IBS/CBS nos itens da nota de origem
[score: 0.758 | camada: 1 | fonte: 03_Regras_Negocio/nota/RN-004-rateio-proporcional-itens.md]

> Contexto diferente (geração notas crédito/débito), mas o PADRÃO de rateio é idêntico ao desta AG.

**Fórmula de proporção (Etapa 1 — idêntica a todos os cenários de rateio):**
```
Participação do item (%) = Valor Total do Item / Valor Total da Nota
```

**Etapa 2 para ICMS:** Redução de BASE de cálculo (não de alíquota como IBS/CBS).

**Exceção (RN-005):** Itens com imposto calculado inferior a R$ 0,01 após rateio não devem ser incluídos. *(Não aplicável nesta AG — os itens já existem no desmembramento.)*

### RN-005 — Item com imposto < R$ 0,01
[score: 0.748 | camada: 1 | fonte: 03_Regras_Negocio/nota/RN-005-item-imposto-menor-centavo.md]
Itens com imposto calculado inferior a R$ 0,01 não devem constar na nota. *(Cenário improvável no desmembramento mas deve ser considerado como edge case.)*

---

## Código Relacionado

### TFItemDesmembramento — uItemDesmembramento.pas
[camada: 2/4 | fonte: App/Mercado/Viasuper/Retaguarda/units/Processos/uItemDesmembramento.pas]

Form de desmembramento. Ponto de entrada via `TFItemDesmembramento.RetornaItemDesmembrado(dmImpNfe, oNotaConf)`.

**Fluxo principal:**
1. `LoadData` — carrega `cdsItem` via `GetDspEdicaoParcialComChaves('ITEMDESMEMBRAMENTO', ...)` parametrizado por IDBANDEIRA, IDITEMFORN, CUSTOUNIT (= VALPRODBRUTO original), ESTAB
2. `CheckFinal` — valida que `SUM(PERCCUSTO) = 100%` (tolerância 0.0001)
3. `actSalvarExecute` — chama `cdsItem.ApplyUpdates(0)` (grava ITEMDESMEMBRAMENTO no banco), depois `FDmImpNFe.InsereProdutosDesmembrados(cdsItem)`
4. Retorna `mrOk` → `DesmembrarProduto1Click` executa `cdsNotaItemAfterPost`

**Campos de `cdsItem`:** IDITEMDES, IDBANDEIRA, IDPESS, IDITEMFORN, IDITEM, QTDE, PERCCUSTO, CUSTOUNIT, DECIMAIS, DESCRICAO, UNIDADE, IDTRIBICMS, DESCTRIBICMS, USAMIX, USALOTE

### TdmImpNfe.InsereProdutosDesmembrados — udmImpNfe.pas:747
[camada: 2/4 | fonte: App/Mercado/Viasuper/Retaguarda/datamodules/udmImpNfe.pas]

**BUG AQUI.** Método que clona e proporciona os registros de impostos.

**Fluxo atual (por iteração do `cds` — desmembramento items):**
1. Localiza original: `cdsNotaItem.Locate('SEQITEM', Seq, [])` e idem para `cdsNotaIcms`, `cdsNotaIpi`, `cdsNotaPis`, `cdsNotaCofins`
2. `ClonaRegistro(cdsNotaItem)` — cria clone com novo SEQITEM (Max+1 via SetNextSeq)
3. `ClonaRegistro(cdsNotaIcms)`, `cdsNotaIpi`, `cdsNotaPis`, `cdsNotaCofins`, `cdsNotaItemImpostoIva`
4. Edita cdsNotaItem com os novos dados do produto desmembrado (IDITEM, QTDE, VALPRODBRUTO = `vProd * PERCCUSTO / 100`, etc.)
5. Edita `cdsNotaIcms`: BASCALC, VALIMP, BASEST, ICMSST × `PERCCUSTO / 100` → `Arredondar(..., 2)`
6. Edita `cdsNotaIpi`: BASCALC (condicional), VALIMP × `PERCCUSTO / 100`
7. Edita `cdsNotaPis`: BASCALC (condicional), VALORPIS × `PERCCUSTO / 100`
8. Edita `cdsNotaCofins`: BASCALC (condicional), VALORCOFINS × `PERCCUSTO / 100`
9. Edita `cdsNotaItemImpostoIva` (IBS/CBS): BASE, VALORIBSUF/VALORCBS × `PERCCUSTO / 100`

**Após o loop:**
- Localiza registros originais (SEQITEM = `Seq`) em cada CDS
- Deleta todos (cdsNotaPis, cdsNotaIcms, cdsNotaIpi, cdsNotaCofins, cdsNotaItemImpostoIva, cdsNotaItem)

**BUG RAIZ — Falta de correção de arredondamento:**
```
Exemplo: VALIMP = R$ 10,00 | 3 itens com PERCCUSTO = 33.33% / 33.33% / 33.34%
  Item 1: Arredondar(10.00 * 33.33/100, 2) = 3.33
  Item 2: Arredondar(10.00 * 33.33/100, 2) = 3.33
  Item 3: Arredondar(10.00 * 33.34/100, 2) = 3.33
  Soma = 9.99 ≠ 10.00 ← PROBLEMA
```

Critério 3.3 exige: diferença (R$ 0,01) vai para o item de maior `VALPRODBRUTO` (último se iguais).

**Arquitetura dos CDSs (importante):**
- `cdsNotaIcms`, `cdsNotaPis`, `cdsNotaCofins` têm `MasterSource = LinkNota` e `MasterFields = 'ESTAB;IDNOTA'`
- São detail de `cdsNota`, NÃO de `cdsNotaItem` — mostram TODOS os registros de impostos da nota corrente
- `ClonaRegistro` copia ESTAB e IDNOTA do original → novos registros ficam visíveis no view filtrado ✓

### TFProcImpNFe.DesmembrarProduto1Click — uProcImpNfe.pas:6071
[camada: 2/4 | fonte: App/Mercado/Viasuper/Retaguarda/units/Processos/uProcImpNfe.pas]

```pascal
procedure TFProcImpNFe.DesmembrarProduto1Click(Sender: TObject);
begin
  inherited;
  if dmImpNfe.cdsNotaItem.IsEmpty then Exit;
  try
    SetNotaItemAfterPost(False);  // desativa AfterPost durante operação
    dmImpNfe.cdsNotaItem.FieldByName('IDITEM').OnChange := NIL;
    TFItemDesmembramento.RetornaItemDesmembrado(dmImpNfe, oNotaConf);
  finally
    SetNotaItemAfterPost(True);
    dmImpNfe.cdsNotaItem.FieldByName('IDITEM').OnChange := cdsNotaItemIDITEMOnValidate;
    cdsNotaItemAfterPost(dmImpNfe.cdsNotaItem);  // atualiza erros/advertências
  end;
end;
```

`cdsNotaItemAfterPost` após o desmembramento: faz PostNotEditModes, VerificaErrosItem, AtualizaErrosCab. **Não recalcula impostos** — os valores ficam como deixados por `InsereProdutosDesmembrados`.

### ClonaRegistro — udmImpNfe.pas:1689
```pascal
// Copia todos os campos do registro atual para um novo registro
// Campo SEQITEM: SetNextSeq → Max(SEQITEM para ESTAB+IDNOTA) + 1
// Campo ALTERADO: 'S'
// Campos ERROS, ADVERTENCIAS: ''
// Campos IDEMBALAGEM, QTDEDAEMB, IDEMBALAGEMDESCRICAO: null
// Demais campos: cópia exata do original
```

---

## Plano Técnico

### Artefatos a modificar
- **`udmImpNfe.pas`** — único arquivo. Método `InsereProdutosDesmembrados` (linha 747).

### Artefatos a criar
- Nenhum.

---

### Bug 1 (PRINCIPAL) — Cursor reposicionado, Edit atua no registro errado

**Causa raiz:** após `ClonaRegistro(cdsNotaIcms)` postar o clone (linha 765), algo entre as linhas 766–835 reposiciona o cursor de `cdsNotaIcms` de volta ao registro **original** (`SEQITEM = Seq`). Quando `cdsNotaIcms.Edit` é chamado na linha 837, ele edita o ORIGINAL — não o clone.

**Efeito observado:**
- 3 clones permanecem com os valores originais intactos
- O original é editado e re-editado com proporções decrescentes a cada iteração (pois o Locate do início de cada iteração o reposiciona), depois deletado ao final
- Resultado: aba ICMS/PIS/COFINS exibe 3 cópias do item original

**Fix — Locate explícito antes de cada Edit:**

Após `ClonaRegistro(cdsNotaIcms)`, salvar o novo `SEQITEM` e usar `Locate` explícito antes do `Edit`. Idem para `cdsNotaIpi`, `cdsNotaPis`, `cdsNotaCofins`.

```pascal
// Após ClonaRegistro(cdsNotaIcms):
nNovaSeqIcms := cdsNotaIcms.AsInt('SEQITEM');
// ... código intermediário ...
// Antes de cdsNotaIcms.Edit (linha 837):
cdsNotaIcms.Locate('SEQITEM', nNovaSeqIcms, []);
cdsNotaIcms.Edit;
```

**Variáveis novas:**
```pascal
nNovaSeqIcms, nNovaSeqIpi, nNovaSeqPis, nNovaSeqCofins: Integer;
```

---

### Bug 2 (SECUNDÁRIO) — Falta de correção de arredondamento

Após corrigir o Bug 1, o proporcionamento passa a funcionar, mas a soma dos valores individualmente arredondados pode diferir do total original em R$ 0,01.

**Exemplo:**
```
VALIMP = R$ 10,00 | 3 itens com 33.33% / 33.33% / 33.34%
  Item 1: Arredondar(10.00 * 33.33/100, 2) = 3.33
  Item 2: Arredondar(10.00 * 33.33/100, 2) = 3.33
  Item 3: Arredondar(10.00 * 33.34/100, 2) = 3.33
  Soma = 9.99 ≠ 10.00
```

**Fix — Correção após o loop:**

1. Antes do loop: capturar valores originais de cada campo
2. Durante o loop: acumular somas e rastrear `nSeqMaxItem` (item de maior `VALPRODBRUTO`; `>=` garante que o último vence quando iguais)
3. Após o loop (antes de deletar originais): aplicar `campo_alvo += (original - soma)` no item de maior valor

**Campos com correção de arredondamento:**

| Dataset | Campos |
|---|---|
| `cdsNotaIcms` | BASCALC, VALIMP, BASEST, ICMSST |
| `cdsNotaPis` | BASCALC, VALORPIS |
| `cdsNotaCofins` | BASCALC, VALORCOFINS |

**Variáveis novas:**
```pascal
vOrigIcmsBas, vOrigIcmsVal, vOrigIcmsBasST, vOrigIcmsST: Double;
vOrigPisBas, vOrigPisVal: Double;
vOrigCofinsBas, vOrigCofinsVal: Double;
vSumIcmsBas, vSumIcmsVal, vSumIcmsBasST, vSumIcmsST: Double;
vSumPisBas, vSumPisVal: Double;
vSumCofinsBas, vSumCofinsVal: Double;
vMaxProd: Double;
nSeqMaxItem: Integer;
```

---

### Estrutura completa do método corrigido (pseudocódigo):

```pascal
procedure TdmImpNfe.InsereProdutosDesmembrados(cds: TVsClientDataSet);
var
  Seq, nNovaSeq: Integer;
  vProd: Double;
  nNovaSeqIcms, nNovaSeqIpi, nNovaSeqPis, nNovaSeqCofins: Integer;
  vOrigIcmsBas, vOrigIcmsVal, vOrigIcmsBasST, vOrigIcmsST: Double;
  vOrigPisBas, vOrigPisVal: Double;
  vOrigCofinsBas, vOrigCofinsVal: Double;
  vSumIcmsBas, vSumIcmsVal, vSumIcmsBasST, vSumIcmsST: Double;
  vSumPisBas, vSumPisVal: Double;
  vSumCofinsBas, vSumCofinsVal: Double;
  vMaxProd: Double;
  nSeqMaxItem: Integer;
begin
  Seq := cdsNotaItem.AsInt('SEQITEM');

  // --- Captura valores originais para correção de arredondamento ---
  cdsNotaIcms.Locate('SEQITEM', Seq, []);
  vOrigIcmsBas   := cdsNotaIcms.AsFloat('BASCALC');
  vOrigIcmsVal   := cdsNotaIcms.AsFloat('VALIMP');
  vOrigIcmsBasST := cdsNotaIcms.AsFloat('BASEST');
  vOrigIcmsST    := cdsNotaIcms.AsFloat('ICMSST');
  cdsNotaPis.Locate('SEQITEM', Seq, []);
  vOrigPisBas := cdsNotaPis.AsFloat('BASCALC');
  vOrigPisVal := cdsNotaPis.AsFloat('VALORPIS');
  cdsNotaCofins.Locate('SEQITEM', Seq, []);
  vOrigCofinsBas := cdsNotaCofins.AsFloat('BASCALC');
  vOrigCofinsVal := cdsNotaCofins.AsFloat('VALORCOFINS');

  // --- Inicializa acumuladores ---
  vSumIcmsBas := 0; vSumIcmsVal := 0; vSumIcmsBasST := 0; vSumIcmsST := 0;
  vSumPisBas  := 0; vSumPisVal  := 0;
  vSumCofinsBas := 0; vSumCofinsVal := 0;
  vMaxProd := -1; nSeqMaxItem := 0;

  cdsNotaItem.AfterPost := nil;
  cds.First;
  while not cds.Eof do
  begin
    cdsNotaItem.Locate('SEQITEM', Seq, []);
    cdsNotaIcms.Locate('SEQITEM', Seq, []);
    cdsNotaIpi.Locate('SEQITEM', Seq, []);
    cdsNotaPis.Locate('SEQITEM', Seq, []);
    cdsNotaCofins.Locate('SEQITEM', Seq, []);

    ClonaRegistro(cdsNotaItem);
    ClonaRegistro(cdsNotaIcms);  nNovaSeqIcms  := cdsNotaIcms.AsInt('SEQITEM');
    ClonaRegistro(cdsNotaIpi);   nNovaSeqIpi   := cdsNotaIpi.AsInt('SEQITEM');
    ClonaRegistro(cdsNotaPis);   nNovaSeqPis   := cdsNotaPis.AsInt('SEQITEM');
    ClonaRegistro(cdsNotaCofins);nNovaSeqCofins := cdsNotaCofins.AsInt('SEQITEM');

    // ... IBS/CBS (sem alteração) ...

    // cdsNotaItem.Edit; ...; cdsNotaItem.Post; (sem alteração)

    // --- Bug 1 fix: Locate explícito antes de cada Edit ---
    cdsNotaIcms.Locate('SEQITEM', nNovaSeqIcms, []);
    cdsNotaIcms.Edit;
    cdsNotaIcms.FieldByName('BASCALC').Value := Arredondar(cdsNotaIcms.AsFloat('BASCALC') * cds.AsFloat('PERCCUSTO') / 100, 2);
    cdsNotaIcms.FieldByName('VALIMP').Value  := Arredondar(cdsNotaIcms.AsFloat('VALIMP')  * cds.AsFloat('PERCCUSTO') / 100, 2);
    cdsNotaIcms.FieldByName('BASEST').Value  := Arredondar(cdsNotaIcms.AsFloat('BASEST')  * cds.AsFloat('PERCCUSTO') / 100, 2);
    cdsNotaIcms.FieldByName('ICMSST').Value  := Arredondar(cdsNotaIcms.AsFloat('ICMSST')  * cds.AsFloat('PERCCUSTO') / 100, 2);
    cdsNotaIcms.Post;

    cdsNotaIpi.Locate('SEQITEM', nNovaSeqIpi, []);
    cdsNotaIpi.Edit; ...; cdsNotaIpi.Post;   // proporcionar BASCALC, VALIMP

    cdsNotaPis.Locate('SEQITEM', nNovaSeqPis, []);
    cdsNotaPis.Edit; ...; cdsNotaPis.Post;   // proporcionar BASCALC, VALORPIS

    cdsNotaCofins.Locate('SEQITEM', nNovaSeqCofins, []);
    cdsNotaCofins.Edit; ...; cdsNotaCofins.Post; // proporcionar BASCALC, VALORCOFINS

    // --- Acumula somas (Bug 2 fix) ---
    vSumIcmsBas   := vSumIcmsBas   + cdsNotaIcms.AsFloat('BASCALC');
    vSumIcmsVal   := vSumIcmsVal   + cdsNotaIcms.AsFloat('VALIMP');
    vSumIcmsBasST := vSumIcmsBasST + cdsNotaIcms.AsFloat('BASEST');
    vSumIcmsST    := vSumIcmsST    + cdsNotaIcms.AsFloat('ICMSST');
    vSumPisBas    := vSumPisBas    + cdsNotaPis.AsFloat('BASCALC');
    vSumPisVal    := vSumPisVal    + cdsNotaPis.AsFloat('VALORPIS');
    vSumCofinsBas := vSumCofinsBas + cdsNotaCofins.AsFloat('BASCALC');
    vSumCofinsVal := vSumCofinsVal + cdsNotaCofins.AsFloat('VALORCOFINS');

    if cdsNotaItem.AsFloat('VALPRODBRUTO') >= vMaxProd then
    begin
      vMaxProd    := cdsNotaItem.AsFloat('VALPRODBRUTO');
      nSeqMaxItem := cdsNotaIcms.AsInt('SEQITEM');  // mesmo SEQITEM do item
    end;

    cds.Next;
  end;

  // --- Bug 2 fix: correção de arredondamento no item de maior valor ---
  cdsNotaIcms.Locate('SEQITEM', nSeqMaxItem, []);
  cdsNotaIcms.Edit;
  cdsNotaIcms.FieldByName('BASCALC').Value := Arredondar(cdsNotaIcms.AsFloat('BASCALC') + (vOrigIcmsBas   - vSumIcmsBas),   2);
  cdsNotaIcms.FieldByName('VALIMP').Value  := Arredondar(cdsNotaIcms.AsFloat('VALIMP')  + (vOrigIcmsVal   - vSumIcmsVal),   2);
  cdsNotaIcms.FieldByName('BASEST').Value  := Arredondar(cdsNotaIcms.AsFloat('BASEST')  + (vOrigIcmsBasST - vSumIcmsBasST), 2);
  cdsNotaIcms.FieldByName('ICMSST').Value  := Arredondar(cdsNotaIcms.AsFloat('ICMSST')  + (vOrigIcmsST   - vSumIcmsST),    2);
  cdsNotaIcms.Post;

  cdsNotaPis.Locate('SEQITEM', nSeqMaxItem, []);
  cdsNotaPis.Edit;
  cdsNotaPis.FieldByName('BASCALC').Value   := Arredondar(cdsNotaPis.AsFloat('BASCALC')   + (vOrigPisBas   - vSumPisBas),   2);
  cdsNotaPis.FieldByName('VALORPIS').Value  := Arredondar(cdsNotaPis.AsFloat('VALORPIS')  + (vOrigPisVal   - vSumPisVal),   2);
  cdsNotaPis.Post;

  cdsNotaCofins.Locate('SEQITEM', nSeqMaxItem, []);
  cdsNotaCofins.Edit;
  cdsNotaCofins.FieldByName('BASCALC').Value    := Arredondar(cdsNotaCofins.AsFloat('BASCALC')    + (vOrigCofinsBas - vSumCofinsBas), 2);
  cdsNotaCofins.FieldByName('VALORCOFINS').Value:= Arredondar(cdsNotaCofins.AsFloat('VALORCOFINS')+ (vOrigCofinsVal - vSumCofinsVal), 2);
  cdsNotaCofins.Post;

  // --- Deleta originais (sem alteração) ---
  cdsNotaIcms.Locate('SEQITEM', Seq, []);
  cdsNotaIpi.Locate('SEQITEM', Seq, []);
  ...
end;
```

---

### Critérios cobertos após o fix:
- **3.1** ✓ — registros reconstruídos corretamente (Bug 1 fix)
- **3.2** ✓ — rateio proporcional por PERCCUSTO (equivalente ao Valor Total da AG)
- **3.3** ✓ — correção de arredondamento no item de maior valor (Bug 2 fix)
- **3.4** ✓ — cancelamento já funciona (sem mudança necessária)

### Impactos colaterais:
- A NF de Entrada gerada na retaguarda usará os valores gravados ao salvar a importação. Com ambos os fixes, os valores individuais por produto serão fiscalmente corretos e o somatório fechará com o total do XML.
- O recálculo marcado na rotina de importação não é afetado (opera sobre os mesmos campos).
