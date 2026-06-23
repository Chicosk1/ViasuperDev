---
id: RN-009
titulo: "Origens de Pedidos no ERP"
tipo: regra-negocio
modulo: "pedido"
status: ativo
criticidade: media
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - pedido
  - compras
  - analise-compra
  - manual
processos_relacionados:
  - PROC-004
  - PROC-007
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Origens de Pedidos no ERP

## 1. Definição

No Viasuper, um pedido de compra pode ser criado por dois caminhos distintos: **automaticamente**, originado pela rotina de Análise de Compra (com base em sugestões de estoque e consumo), ou **manualmente**, lançado diretamente pelo usuário na rotina de Pedidos. A origem do pedido impacta o seu estado inicial e o fluxo de aprovação aplicável.

Esta regra se aplica a todos os documentos do tipo **Pedido de Compra**, **Cotação** e seus estados derivados no ERP.

## 2. Contexto

A distinção entre pedidos automáticos e manuais é fundamental para o processo de governança de compras. Pedidos gerados pela Análise de Compra podem ser submetidos a um fluxo de aprovação gerencial antes de se tornarem efetivos, enquanto pedidos lançados manualmente geralmente entram direto no estado "Pendente" — dependendo da parametrização de aprovação da empresa. Conhecer a origem permite rastrear a causa-raiz de um pedido e validar se ele foi planejado ou é uma compra de emergência.

## 3. Condição (Se / Então)

**Origem 1 — Análise de Compra (Automática):**
- **Se:** o pedido é gerado pela rotina *Processos > Análise de Compra*, com base nos cálculos de sugestão de estoque;
- **Então:**
  - O sistema registra a origem como "Análise de Compra" no cabeçalho do pedido.
  - O pedido pode entrar no estado **"Aguardando Aprovação"** se o fluxo de aprovação estiver configurado para o tipo de documento.
  - O histórico do pedido preserva o vínculo com a análise que o originou.

**Origem 2 — Lançamento Manual:**
- **Se:** o usuário cria um novo pedido diretamente pela tela *Processos > Pedido > Pedidos*, clicando em "Abrir Vazio";
- **Então:**
  - O sistema registra a origem como "Manual".
  - O pedido nasce no estado **"Pendente"** diretamente, sem passar pelo fluxo de sugestão automática.
  - O usuário é inteiramente responsável pelo preenchimento das quantidades, fornecedores e itens.

## 4. Exemplos

### Válido — Pedido automático gerado pela Análise de Compra

1. Comprador acessa *Processos > Análise de Compra*.
2. Seleciona fornecedor "Distribuidora X", marca 12 produtos com sugestão positiva.
3. Confirma e o sistema gera pedido de compra nº 1.023 com status "Aguardando Aprovação".
4. Gerente aprova o pedido → status muda para "Pendente".

### Válido — Pedido manual de emergência

1. Comprador percebe ruptura de um produto não incluso no mix regular.
2. Acessa *Processos > Pedido > Pedidos* e clica em "Abrir Vazio".
3. Informa o fornecedor e o item manualmente.
4. Salva → pedido nasce como "Pendente" diretamente.

### Inválido

Alterar retroativamente a origem de um pedido (de "Manual" para "Análise de Compra" ou vice-versa) após a sua geração. O sistema não prevê essa operação e o histórico de rastreabilidade seria comprometido.

## 5. Exceções

- Pedidos de **cotação** seguem o mesmo fluxo de origem (automática ou manual), mas permanecem no estado "Cotação de Compra" até a sua conversão em pedido efetivo.
- Pedidos de **transferência** gerados pelo Pedido Centralizado possuem origem própria (vinculada ao pedido centralizador pai) e são governados pela [[RN-011-parametrizacao-transferencia]].

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| Configuração de Aprovação de Pedido | Ativo/Inativo no tipo de documento | Define se pedidos automáticos entram em "Aguardando Aprovação" |
| Tipo de Documento (Conf. de Pedido) | Pedido de Compra / Cotação | Determina o comportamento e estados disponíveis |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Pedidos e Análise de Compra |
