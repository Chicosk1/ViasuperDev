---
id: RN-018
titulo: "Integração de Pedidos da Retaguarda com a Frente de Caixa (PDV)"
tipo: regra-negocio
modulo: "pdv"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - pdv
  - pedido
  - integracao
  - retaguarda
  - frente-de-caixa
processos_relacionados:
  - PROC-004
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Integração de Pedidos da Retaguarda com a Frente de Caixa (PDV)

## 1. Definição

Para que um pedido lançado na **Retaguarda** (ERP Viasuper) seja visualizado, faturado e entregue na **Frente de Caixa** (PDV), a **Configuração de Pedido** vinculada ao documento deve ter o parâmetro **"Envia para PDV"** configurado como **"SIM"**. Sem essa configuração, o pedido permanece apenas na retaguarda e não é sincronizado com os terminais de ponto de venda.

Esta regra se aplica a todos os tipos de pedidos que precisam ser finalizados/entregues no PDV, como pedidos de venda para clientes, entregas de balcão, pedidos de delivery, etc.

## 2. Contexto

O ERP Viasuper opera com uma arquitetura de retaguarda + frente de caixa onde os sistemas trocam dados de forma controlada. Nem todos os pedidos precisam chegar ao PDV — pedidos de compra de fornecedores, transferências internas e pedidos internos da empresa permanecem na retaguarda. Apenas os pedidos destinados ao faturamento ao consumidor final (ou ao cliente pessoa jurídica na frente de loja) precisam ser visibilizados nos terminais de PDV. A parametrização explícita do "Envia para PDV" evita que pedidos internos poluam a fila de pedidos do caixa.

## 3. Condição (Se / Então)

- **Se:** um pedido é criado na Retaguarda com um tipo de documento onde "Envia para PDV" = **SIM**;
- **Então:**
  1. O sistema sincroniza o pedido (cabeçalho + itens + dados do cliente) para o banco de dados local ou compartilhado do PDV.
  2. O pedido aparece na fila de pedidos do terminal de caixa selecionado (ou de todos os terminais da loja, conforme configuração).
  3. O operador de caixa pode abrir o pedido, verificar os itens, registrar o pagamento e emitir o cupom fiscal (NFC-e) ou nota fiscal ao consumidor.
  4. Após o faturamento no PDV, o status do pedido na Retaguarda é atualizado automaticamente para *"Totalmente Entregue"*.

- **Se:** "Envia para PDV" = **NÃO** (ou não configurado);
- **Então:**
  1. O pedido permanece visível apenas na Retaguarda.
  2. O pedido **não** aparece nos terminais de PDV.
  3. A finalização/faturamento deve ocorrer integralmente na Retaguarda.

## 4. Exemplos

### Válido — Pedido de entrega em domicílio (delivery)

1. Atendente registra pedido do cliente na Retaguarda com tipo "Pedido de Venda Delivery" (Envia para PDV = SIM).
2. PDV da loja exibe o pedido na fila de entregas.
3. Caixa fatura o pedido, emite NFC-e e o entregador leva a mercadoria.
4. Status na Retaguarda: *"Totalmente Entregue"*.

### Válido — Pedido de compra de fornecedor (não vai para o PDV)

Pedido de compra de 500 kg de açúcar. Tipo "Pedido de Compra" (Envia para PDV = NÃO).
- O pedido não aparece nos terminais de caixa.
- A recepção é feita via *Processos > Pedido > Recepção de Pedidos* na Retaguarda.

### Inválido

Configurar "Envia para PDV = SIM" em tipos de pedido destinados exclusivamente à Retaguarda (ex: pedidos de transferência interna), causando poluição na fila de pedidos dos terminais de caixa e confusão operacional.

## 5. Exceções

- A sincronização entre Retaguarda e PDV depende da infraestrutura de rede local. Em caso de queda de conexão, o pedido pode não aparecer no PDV até que a sincronização seja restabelecida.
- Pedidos editados na Retaguarda após a sincronização inicial podem não refletir imediatamente no PDV — depende do intervalo de sincronização configurado no SyncJet ou no serviço de integração.
- Pedidos cancelados na Retaguarda devem ser removidos da fila do PDV automaticamente pelo processo de sincronização.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| "Envia para PDV" | Configurações > Documentos > Configurações de Pedido | Define se o tipo de pedido é sincronizado com o PDV |
| Terminal de PDV de destino | Configurações > PDV > Terminais | Define para quais caixas o pedido é enviado |
| Intervalo de sincronização | Configurações > SyncJet / Integração PDV | Define a frequência de atualização da fila de pedidos nos terminais |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base no PDF de Pedidos (rotina de Processos > Pedido) |
