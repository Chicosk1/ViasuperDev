---
id: RN-017
titulo: "Desmembramento de Produtos na Entrada de Nota Fiscal"
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
  - produto
  - desmembramento
  - nota-fiscal
  - importacao-xml
  - estoque
processos_relacionados:
  - PROC-002
  - PROC-003
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Desmembramento de Produtos na Entrada de Nota Fiscal

## 1. Definição

O **desmembramento de produtos** é o mecanismo pelo qual um item originado de um fornecedor (identificado pelo código/descrição do fornecedor no XML) é fracionado e vinculado a **um ou mais produtos internos** do catálogo do ERP. Isso permite que uma única linha do XML do fornecedor alimente múltiplos SKUs internos da loja — por exemplo, um fardo de 12 unidades do fornecedor sendo desmembrado em 12 unidades do produto individual vendido no varejo.

Esta regra se aplica à rotina de **Importação de NF-e**, **Lançamento Manual de Notas Fiscais** e qualquer fluxo de entrada de mercadoria que necessite mapear itens de fornecedor para o catálogo interno do ERP.

## 2. Contexto

Fornecedores frequentemente vendem em embalagens distintas das unidades de venda ao consumidor (caixas, fardos, pacotes múltiplos). O ERP precisa registrar a entrada no estoque na unidade correta de cada produto interno. Além disso, um mesmo produto pode ter múltiplos códigos no ERP (código interno + código de barras + código do fornecedor). O desmembramento garante que a tributação do item do fornecedor seja preservada e redistribuída corretamente entre os produtos internos gerados.

## 3. Condição (Se / Então)

**Vinculação de código do fornecedor a produto interno:**
- **Se:** ao importar um XML, o sistema identifica um item (por NCM, código de barras ou código do fornecedor) que está vinculado a um produto interno no cadastro de produtos;
- **Então:**
  1. O sistema substitui automaticamente o código/descrição do fornecedor pelo código/descrição interno do produto.
  2. Aplica o fator de conversão de embalagem (ex: 1 fardo fornecedor = 12 unidades internas).
  3. Movimenta o estoque do produto interno com a quantidade convertida.
  4. A tributação (ICMS, IPI, PIS, COFINS) é herdada do item do XML e redistribuída proporcionalmente entre os produtos internos gerados.

**Desmembramento em múltiplos SKUs:**
- **Se:** um item do XML corresponde a N produtos internos (ex: kit com produtos distintos);
- **Então:**
  1. O sistema abre a tela de desmembramento, listando os produtos internos e suas quantidades sugeridas.
  2. O usuário confirma ou ajusta o desmembramento.
  3. Cada produto interno recebe sua parcela de custo e tributação proporcionalmente.
  4. O estoque de cada produto interno é movimentado individualmente.

## 4. Exemplos

### Válido — Fardo com conversão de unidade

XML do fornecedor: 10 fardos de Cerveja 350ml (cód. fornecedor: 9876)
- Produto interno: Cerveja 350ml un (cód. interno: 1234)
- Fator de conversão: 1 fardo = 24 unidades
- Resultado: entrada de 240 un no produto 1234

### Válido — Produto novo sem vínculo no ERP

XML traz código de produto do fornecedor que não existe no ERP. O sistema exibe a tela de vinculação, onde o usuário:
1. Busca o produto interno correspondente.
2. Define o fator de conversão.
3. O sistema salva o vínculo para reutilização em futuras importações do mesmo fornecedor.

### Inválido

Lançar a entrada com o código do fornecedor diretamente no estoque interno sem criar o vínculo — isso geraria itens "soltos" no estoque sem código de barras para venda no PDV e sem precificação correta.

## 5. Exceções

- Produtos que são vendidos na mesma unidade do fornecedor (ex: produtos unitários) não requerem desmembramento. O vínculo é 1:1 sem fator de conversão.
- Se o produto não tiver código cadastrado no ERP, o usuário deve primeiro cadastrar o produto e depois realizar a vinculação/desmembramento.
- O desmembramento não é necessário quando o XML já vem com o código de barras do produto unitário — nesse caso, o sistema vincula automaticamente pelo EAN/GTIN.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Código do Fornecedor no Produto | Cadastro do Produto > Embalagens/Fornecedores | Vínculo entre código do fornecedor e produto interno |
| Fator de Conversão | Cadastro do Produto > Embalagens | Define quantas unidades internas equivalem a 1 unidade do fornecedor |
| Código de Barras (EAN/GTIN) | Cadastro do Produto | Chave alternativa de busca automática na importação do XML |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base no PDF de Importação NF-e |
