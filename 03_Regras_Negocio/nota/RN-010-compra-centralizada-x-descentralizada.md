---
id: RN-010
titulo: "Modalidade de Compra Centralizada x Descentralizada"
tipo: regra-negocio
modulo: "pedido"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - pedido
  - centralizado
  - descentralizado
  - rede
  - filiais
  - transferencia
processos_relacionados:
  - PROC-005
  - PROC-007
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Modalidade de Compra Centralizada x Descentralizada

## 1. Definição

Ao executar a rotina de **Pedido Centralizado** ou **Análise de Compra** para múltiplos estabelecimentos, o sistema oferece duas modalidades de operação logística e fiscal:

- **Compra Centralizada:** Todo o volume de compra é consolidado em um único pedido emitido contra o **estabelecimento central** (matriz ou CD). O fornecedor entregará tudo em um único ponto. O rateio e a distribuição entre filiais ocorrem internamente via pedidos de transferência.
- **Compra Descentralizada:** O sistema fragmenta o pedido e gera documentos de compra individuais, emitidos diretamente contra cada **filial de destino**. Cada loja negocia e recebe diretamente do fornecedor.

A escolha da modalidade impacta diretamente o número e o destino dos pedidos gerados, os impostos aplicados e o fluxo logístico pós-compra.

## 2. Contexto

Redes de supermercado com múltiplas lojas precisam definir uma estratégia de abastecimento. A compra centralizada maximiza o poder de negociação (volume maior = melhores preços) e facilita o controle de estoque, mas exige uma estrutura de CD e logística de distribuição interna. A compra descentralizada é mais simples operacionalmente, mas pode resultar em condições comerciais piores com fornecedores. A parametrização desta regra no ERP determina como os pedidos serão gerados e qual carga tributária será aplicada em cada documento.

## 3. Condição (Se / Então)

**Modalidade Centralizada:**
- **Se:** o usuário marca a opção *"Realizar Compra Centralizada"* na tela de Pedido Centralizado ou Análise de Compra;
- **Então:**
  - O sistema gera **um único pedido de compra** com o estabelecimento central como destinatário.
  - As quantidades de todas as filiais selecionadas são somadas neste pedido.
  - Opcionalmente, o sistema gera pedidos de transferência (saída do CD → entrada nas filiais).
  - A nota fiscal de compra é emitida pelo fornecedor contra o CNPJ do estabelecimento central.

**Modalidade Descentralizada:**
- **Se:** o usuário **não** marca a opção *"Realizar Compra Centralizada"*;
- **Então:**
  - O sistema gera **um pedido de compra por estabelecimento de destino** selecionado.
  - Cada pedido tem como destinatário o CNPJ da filial respectiva.
  - O fornecedor emite notas fiscais individuais para cada filial.
  - Não há geração de pedidos de transferência interna.

## 4. Exemplos

### Válido — Rede com 3 lojas usando compra centralizada

Comprador seleciona 50 un de Arroz para Loja A, 30 para Loja B e 20 para Loja C:
- **Resultado Centralizado:** 1 pedido de compra de 100 un para o CD. Sistema gera 3 pedidos de transferência: CD → Loja A (50), CD → Loja B (30), CD → Loja C (20).
- **Resultado Descentralizado:** 3 pedidos de compra: Loja A (50 un), Loja B (30 un), Loja C (20 un). Fornecedor entrega em cada loja separadamente.

### Inválido

Misturar as modalidades no mesmo processo de compra — ex: gerar um pedido centralizado para alguns produtos e descentralizados para outros no mesmo lote. A rotina não suporta essa configuração mista e o usuário deve executar processos separados.

## 5. Exceções

- A opção de compra centralizada exige que o **Mix de Produtos por Estabelecimento** esteja corretamente configurado para os produtos e filiais envolvidos.
- A geração de pedidos de transferência só ocorre se o usuário também marcar a opção *"Realizar Pedidos de Transferência"* no mesmo fluxo.
- Filiais sem Mix de Produtos configurado podem não aparecer nas opções de distribuição.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| Checkbox "Realizar Compra Centralizada" | Marcado / Desmarcado | Define se gera 1 pedido (CD) ou N pedidos (filiais) |
| Checkbox "Realizar Pedidos de Transferência" | Marcado / Desmarcado | Ativa geração de pedidos de transferência CD → Filiais |
| Conf. Documento Padrão (Transf. Entrada/Saída) | Configurado em Configurações > Gerais | Base tributária e operacional dos pedidos de transferência |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Pedido Centralizado e Análise de Compra |
