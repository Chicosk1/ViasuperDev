---
id: RN-013
titulo: "Recálculo Tributário de Documentos Fiscais"
tipo: regra-negocio
modulo: "fiscal"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - fiscal
  - icms
  - ibs
  - cbs
  - impostos
  - nota-fiscal
  - pedido
  - recalculo
processos_relacionados:
  - PROC-002
  - PROC-003
  - PROC-004
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Recálculo Tributário de Documentos Fiscais

## 1. Definição

O sistema permite que o usuário solicite explicitamente o **recálculo dos impostos** de um documento fiscal (nota fiscal ou pedido) após a sua criação ou importação. Quando acionado, o ERP desconsidera as alíquotas e bases originais (vindas do XML do fornecedor ou do rascunho inicial) e recalcula os tributos aplicando as **configurações fiscais vigentes** cadastradas no ERP para cada produto e operação — incluindo ICMS, IBS, CBS, PIS, COFINS e IPI.

Esta regra se aplica a notas fiscais de entrada, pedidos de compra, documentos importados via XML (NF-e) e qualquer outro documento fiscal do ERP que ofereça a função de recálculo de impostos.

## 2. Contexto

As alíquotas tributárias mudam com frequência (legislação estadual, acordos entre estados, reforma tributária). Um XML importado de fornecedor pode trazer alíquotas desatualizadas ou incorretas para a realidade fiscal do destinatário. Também é comum que o usuário crie um pedido com determinadas configurações e, após negociação ou mudança de CFOP, precise ajustar toda a tributação sem recriar o documento do zero. O recálculo tributário resolve esses cenários de forma centralizada, preservando os dados comerciais (quantidades, preços) e atualizando apenas o bloco fiscal.

## 3. Condição (Se / Então)

- **Se:** o usuário aciona a função "Recalcular Impostos" em um documento fiscal ou pedido no ERP;
- **Então:**
  1. O sistema percorre todos os itens do documento.
  2. Para cada item, consulta as **tabelas de tributação** do ERP (alíquotas de ICMS, IBS/CBS por NCM, PIS/COFINS, IPI, Funrural, etc.) com base no:
     - NCM do produto.
     - CFOP da operação.
     - UF de origem e destino.
     - Regime tributário do emitente e destinatário.
  3. Substitui as alíquotas e bases de cálculo existentes pelas novas calculadas.
  4. Recalcula os valores de imposto de cada item e atualiza os totalizadores do cabeçalho do documento.
  5. Os campos comerciais (quantidade, preço unitário, descontos) **não** são alterados pelo recálculo.

## 4. Exemplos

### Válido — XML importado com ICMS desatualizado

Fornecedor de SP emite NF com ICMS 12% para destinatário no PR. Após atualização do protocolo ICMS, a alíquota correta passou a ser 7%. O usuário importa o XML, verifica a inconsistência e aciona "Recalcular Impostos". O sistema aplica os 7% corretos baseado nas tabelas do ERP.

### Válido — Pedido criado antes de mudança de NCM

Um pedido de compra foi criado com ICMS de 12%. O produto teve seu NCM reclassificado para uma alíquota de 4%. Antes de recepcionar a NF, o comprador aciona o recálculo e o pedido é atualizado para 4%.

### Inválido

Utilizar o recálculo para alterar o preço de custo dos itens ou as quantidades do pedido. O recálculo é restrito ao bloco tributário e não interfere nos valores comerciais do documento.

## 5. Exceções

- Documentos **emitidos/autorizados** na SEFAZ (com número de NF já atribuído e DANFE gerado) não permitem recálculo após a autorização. Qualquer correção deve ser feita via nota de correção ou carta de correção eletrônica.
- Se as tabelas de tributação do ERP estiverem desatualizadas (NCM sem alíquota cadastrada), o recálculo pode retornar imposto zero para o item.
- O recálculo de IBS/CBS segue a [[RN-003-calculo-base-ajuste-ibs-cbs]] quando aplicável (reforma tributária).

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Tabela de tributação ICMS | Configurações > Fiscal > Tributação | Define alíquotas por NCM e UF origem/destino |
| Tabela IBS/CBS | Configurações > Fiscal > IVA | Define alíquotas para a reforma tributária |
| CFOP da operação | Cabeçalho do documento | Determina a natureza fiscal e as regras aplicáveis |
| Regime tributário | Cadastro da empresa/estabelecimento | Influi nas alíquotas de PIS/COFINS (Lucro Real vs. Presumido vs. Simples) |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Importação NF-e, Nota Fiscal e Pedidos |
