---
id: PROC-008
titulo: "Recepção de Pedidos"
tipo: processo
modulo: "pedido"
sistema: viasuper
versao_sistema: "1.0.2105"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - pedido
  - recepcao
  - viasuper
rns_relacionadas:
  - RN-012
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-18"
data_revisao: "2026-06-18"
---

# Recepção de Pedidos

## 1. Objetivo

Realizar a recepção lógica dos pedidos de compra pendentes gerados no ERP. A rotina permite que o usuário localize um ou múltiplos pedidos de um mesmo fornecedor e realize a conversão dos mesmos em uma Nota Fiscal (Recepção), que servirá de base para a entrada da mercadoria e o fluxo de pagamento financeiro.

## 2. Pré-condições

- Existência de pedidos de compra ativos e com status `Pendente` ou `Parcialmente Entregue` para o fornecedor pesquisado.
- Parâmetros tributários e de pessoa do fornecedor atualizados.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina incluem:

- RN-045-fornecedor-obrigatorio-recepcao — **Fornecedor Obrigatório:** A consulta no filtro principal exige o preenchimento obrigatório da pessoa/fornecedor emissor do pedido.
- [[RN-012-geracao-nota-recepcao]] — **Seleção Múltipla e Conversão em NF:** O sistema permite a marcação de múltiplos pedidos de compra listados no grid do mesmo fornecedor. Ao salvar, todos os itens selecionados são convertidos e agrupados em um único lançamento de rascunho de Nota Fiscal.

## 4. Fluxo do Processo

### 4.1. Consulta e Seleção de Pedidos

1. Acessar o menu **Processos > Pedido > Recepção de Pedidos**.
2. No painel de parâmetros superior, preencher os filtros:
   - **Fornecedor:** Obrigatório. Informar o código interno ou utilizar a busca para definir o fornecedor.
   - (Opcional) Cód. Pedido Entrega.
   - (Opcional) Data do Pedido e Validade.
   - (Opcional) Previsão de Entrega.
3. Clicar no botão **Executar**.
4. O sistema carregará o grid principal **"Cabeçalho do(s) Pedido(s)"** exibindo todos os registros correspondentes aos filtros (incluindo Situação do pedido e Configuração de Documento base).
5. Ao clicar sobre uma linha (um pedido), o sistema preencherá o grid inferior **"Produto(s) do(s) Pedido(s)"** detalhando as mercadorias, quantidades, valor unitário, saldo a entregar e totais.

---

### 4.2. Geração da Recepção (Nota Fiscal)

1. Marcar o checkbox (coluna `[X]`) ao lado dos pedidos que deseja recepcionar no grid superior. (É possível utilizar a opção *Marcar Todos*).
2. Revisar as quantidades que serão recebidas no grid inferior.
3. Clicar no botão **Salvar**.
4. O sistema automaticamente utilizará as informações dos pedidos para gerar o cabeçalho e os itens de uma Nota Fiscal (tela de rascunho de nota).
5. O usuário é redirecionado para a tela da Nota Fiscal de Entrada. Nela, o usuário deverá:
   - Validar as abas de Detalhes, Transporte, Impostos e Rateios.
   - Validar a aba de **Pagamento** informando ou conferindo os boletos/duplicatas e o valor do frete/desconto se necessário.
6. Clicar em **Salvar** na tela da Nota Fiscal.
7. A recepção estará concluída, os estoques dos itens serão movimentados e o saldo do pedido original de compra passará para a situação *Totalmente Entregue* (ou Parcial, se houve recebimento inferior ao comprado).

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** `Processos > Pedido > Recepção de Pedidos`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:** [Não informado]
- **Tabelas envolvidas:** 
  - `PEDIDO`
  - `PEDIDOITEM` (Origem)
  - `NOTA`
  - `NOTAITEM` (Destino/Recepção)
  - `PESSOADOC` (Filtro de fornecedor)
- **Consultas envolvidas:** [Não informado]
- **Arquitetura de referência:** [Não informado]

## 6. Casos de Falha

### Pedido de compra não aparece no grid
- **Sintoma:** Após preencher o fornecedor e clicar em executar, o pedido desejado não é exibido na lista.
- **Causa:** O pedido pode já estar na situação "Totalmente Entregue", cancelado, vencido, ou pertencer a um fornecedor distinto do informado. Outra possibilidade é que a data de previsão de entrega seja muito fora dos filtros informados.
- **Solução:** Checar a real situação do pedido na rotina "Processos > Pedido > Pedidos".

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-18 | 1.0.2105 | Criação inicial e documentação da rotina de Recepção de Pedidos. |
