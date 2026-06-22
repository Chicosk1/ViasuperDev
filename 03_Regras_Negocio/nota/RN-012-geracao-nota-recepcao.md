---
id: RN-012
titulo: "Conversão de Múltiplos Pedidos em Nota Fiscal de Recepção"
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
  - recepcao
  - nota-fiscal
  - fornecedor
  - entrada
processos_relacionados:
  - PROC-003
  - PROC-008
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Conversão de Múltiplos Pedidos em Nota Fiscal de Recepção

## 1. Definição

Na rotina de **Recepção de Pedidos**, o sistema permite que o usuário selecione **um ou mais pedidos de compra** do mesmo fornecedor e converta todos eles em **um único documento fiscal de entrada** (Nota Fiscal de Recepção). Este agrupamento simplifica o processo de entrada de mercadoria quando o fornecedor entrega múltiplos pedidos em uma mesma visita ou emite uma NF única consolidando vários pedidos.

Esta regra se aplica à rotina *Processos > Pedido > Recepção de Pedidos* e a qualquer rotina do ERP que realize a conversão de pedidos de compra em nota fiscal de entrada.

## 2. Contexto

Em operações de supermercado, é comum que um fornecedor entregue múltiplos pedidos de uma vez (ex: pedido da semana passada + pedido desta semana), emitindo uma única nota fiscal consolidada. Processar cada pedido em uma nota separada seria ineficiente e geraria inconsistências no financeiro e no estoque. O ERP permite o agrupamento lógico de pedidos do mesmo fornecedor em um único lançamento de recepção, desde que compartilhem o mesmo CNPJ de origem.

## 3. Condição (Se / Então)

- **Se:** o usuário seleciona dois ou mais pedidos de compra no grid da Recepção de Pedidos e clica em "Salvar";
- **Então:**
  1. O sistema valida que todos os pedidos selecionados pertencem ao **mesmo fornecedor**.
  2. O sistema consolida os itens de todos os pedidos selecionados em um único cabeçalho de Nota Fiscal de entrada.
  3. Itens repetidos (mesmo código de produto em pedidos diferentes) são somados ou mantidos em linhas separadas, dependendo da configuração do documento.
  4. O usuário é redirecionado para a tela de Nota Fiscal de Entrada com os dados pré-preenchidos, devendo informar o **número do documento** (NF do fornecedor), série e datas.
  5. Os pedidos selecionados passam para o status *"Totalmente Entregue"* ou *"Parcialmente Entregue"* conforme a quantidade recepcionada vs. a quantidade pedida.

## 4. Exemplos

### Válido — 2 pedidos do mesmo fornecedor agrupados em 1 NF

Fornecedor: Distribuidora ABC (CNPJ: 12.345.678/0001-99)
- Pedido 1.001: 50 un de Arroz Tipo 1
- Pedido 1.008: 30 un de Feijão Carioca

Usuário seleciona ambos na Recepção de Pedidos → sistema gera uma NF de entrada com 2 linhas de produto. Fornecedor entregou com NF nº 5.432 → usuário informa o número e salva.

### Inválido — Pedidos de fornecedores distintos

Tentar selecionar simultaneamente pedidos da "Distribuidora ABC" e do "Fornecedor XYZ" para gerar uma única NF. O sistema deve impedir essa operação, pois uma nota fiscal de entrada só pode ter um único CNPJ emitente.

### Caso de Recebimento Parcial

Pedido 1.001 com 50 un de Arroz, mas o fornecedor entregou apenas 30 un:
- O usuário ajusta a quantidade na tela de recepção para 30 un.
- Sistema gera NF com 30 un.
- Pedido 1.001 passa para status *"Parcialmente Entregue"* (saldo de 20 un em aberto).

## 5. Exceções

- Pedidos com status *"Totalmente Entregue"* ou *"Cancelado"* não aparecem no grid de seleção da Recepção de Pedidos.
- A recepção parcial não fecha o pedido — o saldo restante continua disponível para uma nova recepção futura.
- Pedidos de **cotação** não podem ser recepcionados diretamente; devem primeiro ser convertidos em pedidos de compra efetivos.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| Fornecedor (filtro) | Obrigatório | Restringe os pedidos exibidos ao fornecedor selecionado |
| Status do Pedido | Pendente ou Parcialmente Entregue | Apenas pedidos nestes estados são exibidos para recepção |
| Número do Documento (NF) | Informado pelo usuário na tela de NF | Identifica o documento fiscal do fornecedor no sistema |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base no PDF de Recepção de Pedidos |
