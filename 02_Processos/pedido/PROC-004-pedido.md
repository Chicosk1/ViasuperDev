---
id: PROC-004
titulo: "Gerenciamento de Pedido e Cotação"
tipo: processo
modulo: "pedido"
sistema: viasuper
versao_sistema: "1.0"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - pedido
  - cotacao
  - compras
  - pdv
  - viasuper
rns_relacionadas: []
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-10"
data_revisao: "2026-06-10"
---

# Gerenciamento de Pedido e Cotação

## 1. Objetivo

Gerenciar o ciclo de vida de pedidos de compra e venda no sistema Viasuper (sejam lançados manualmente ou importados da análise de compra), permitindo também o controle de cotações com múltiplos fornecedores via arquivos de planilha (`.xls`) e a integração de pedidos para faturamento e entrega na frente de caixa (PDV).

## 2. Pré-condições

- Cadastro de Pessoas (Fornecedores, Clientes e Comissionados) devidamente atualizado.
- Cadastro de Produtos ativo no sistema Retaguarda.
- Parametrizações tributárias configuradas para o recálculo dos itens.
- Configuração de Pedido ativa (com a opção *"Envia para PDV"* marcada como *"SIM"* se o pedido for finalizado na frente de caixa).
- Contas de e-mail dos fornecedores vinculadas em seus respectivos cadastros de pessoa para o fluxo de cotações.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina de Pedidos e Cotações incluem:

- RN-00x-origem-pedidos — **Origem dos Pedidos:** Os pedidos de compra podem ser gerados de forma automatizada por meio da rotina de análise de compra ou criados manualmente pelo usuário na rotina de lançamentos.
- RN-00x-comissionamento-pedido — **Vínculo de Comissionados:** A comissão do pedido está estritamente vinculada ao cadastro prévio da pessoa comissionada na aba "Cliente" dentro da rotina de Cadastro de Pessoas.
- RN-00x-situacao-pedido-cotacao — **Estados e Situações do Pedido:** O ciclo de vida do pedido ou cotação obedece às seguintes situações:
  - *Aguardando Aprovação:* Pedidos gerados via análise de compra que necessitam de liberação do gestor.
  - *Pendente:* Pedido aprovado, mas ainda sem recebimento ou faturamento.
  - *Parcialmente Entregue:* Recebimento ou faturamento parcial dos produtos do pedido.
  - *Totalmente Entregue:* Pedido cujo saldo de itens foi 100% recebido/faturado.
  - *Cotação de Compra:* Estado inicial de negociação com fornecedores.
  - *Cotação Finalizada:* Cotação encerrada que originou um ou mais pedidos de compra.
- RN-00x-envio-pdv-integracao — **Integração Retaguarda e Frente de Caixa (PDV):** Para que um pedido lançado na Retaguarda seja visualizado e entregue pelo PDV, a respectiva Configuração de Pedido (*Configurações > Documentos > Configurações de Pedido*) deve ter o parâmetro *"Envia para PDV"* configurado como *"SIM"*.
- RN-00x-cotacao-fornecedores-email — **Exportação e Envio de Planilhas de Cotação:** A rotina de cotações permite gerar e enviar planilhas no formato `.xls` por e-mail para múltiplos fornecedores vinculados, exigindo endereço de correio eletrônico cadastrado na ficha do fornecedor.
- RN-00x-sugestao-melhor-fornecedor — **Homologação pelo Menor Valor Global:** O sistema analisa os retornos das planilhas importadas e sugere na aba "Melhor Fornecedor" aquele que apresenta o menor custo total somado para todos os itens da cotação.
- RN-00x-sugestao-melhor-preco-item — **Homologação pelo Menor Preço por Item:** O sistema classifica individualmente por item o participante com o menor preço proposto, permitindo fracionar o faturamento e gerar múltiplos pedidos de compra direcionados.
- RN-00x-recalculo-tributacao-pedido — **Recálculo de Impostos no Pedido:** Caso haja alterações nas configurações e alíquotas fiscais do ERP após o lançamento do pedido, o sistema permite recalcular e ajustar os impostos dos itens a qualquer momento antes da finalização e faturamento do pedido.

## 4. Fluxo do Processo

### 4.1. Consulta e Filtro de Pedidos/Cotações

1. Acessar o menu **Processos > Pedido > Pedidos**.
2. Na tela de filtros:
   - Selecionar o tipo de consulta (**Pedidos** ou **Cotação**).
   - Informar os filtros desejados para a pesquisa (*número do pedido, data de emissão, código da pessoa ou nome da pessoa*).
3. Clicar em **OK**.
4. O sistema carregará o grid com os dados da consulta (*código do pedido, data, pessoa, situação e usuário de inclusão*).
5. Para consultar os detalhes de um pedido, efetuar duplo clique sobre o registro desejado.
6. Para criar um novo pedido a partir desta tela, clicar no botão **Incluir** (ou clicar em **Abrir Vazio** na tela de filtros).

---

### 4.2. Lançamento e Finalização Manual de Pedido

1. Na tela principal de pedidos, informar a **Configuração** do pedido (tecle **F3** para busca rápida).
2. Informar a **Pessoa** associada ao pedido (busca por F3, CPF/CNPJ ou código interno). O comissionado e dados fiscais serão carregados automaticamente.
3. Na aba **1-Produtos**, inserir os itens informando a descrição/código do produto, a quantidade e o valor unitário.
4. (Opcional) Navegar pelas abas para conferir as demais informações do pedido:
   - **Aba 2-Detalhes:** Visualização do usuário de inclusão e a origem do documento.
   - **Aba 3-Impostos:** Conferência da tributação aplicada aos itens.
   - **Aba 4-Fornecedor:** Conferência dos dados cadastrais do fornecedor.
   - **Aba 5-Transporte:** Dados da transportadora, frete e endereço de entrega física.
   - **Aba 6-Previsão de Entrega:** Lançar previsões de entrega globais ou por produto e clicar em **Salvar Previsão**.
   - **Aba 7-Previsão de Pagamento:** Definir prazos, parcelamentos e formas de pagamento.
5. Se o pedido for gerado via análise de compra e estiver na situação **Aguardando Aprovação**, clicar no botão de **Aprovação** para liberá-lo para a situação **Pendente** (ou para **Cancelar** o pedido).
6. Clicar no botão **Salvar** no cabeçalho do pedido.

---

### 4.3. Fluxo de Cotação de Compra com Fornecedores

1. Na tela de pedidos, selecionar a configuração de pedido correspondente a **Cotação de Compra**.
2. Na aba **1-Produtos**, preencher o grid com os itens que serão cotados.
3. Clicar no botão **Análise** para carregar a tela de cotações.
4. Na aba **Fornecedores**:
   - Clicar em **Incluir** para selecionar os fornecedores participantes da cotação.
   - Clicar em **Exportar** para gerar o arquivo `.xls` consolidado dos itens.
   - Marcar os fornecedores desejados no grid e clicar em **Enviar E-mail** para despachar as planilhas.
5. Recepcionar os arquivos `.xls` preenchidos pelos fornecedores via e-mail e salvá-los localmente no computador.
6. Na tela de análise de cotação do Viasuper, clicar em **Importar** e localizar os arquivos retornados pelos fornecedores.
7. Analisar as propostas por meio das abas de comparação:
   - **Aba Produtos x Fornecedores:** Visualização individualizada de cada produto com os preços propostos por cada participante.
   - **Aba Melhor Fornecedor:** Apresenta o fornecedor com a menor cotação total global. O usuário pode homologar a sugestão ou selecionar outro fornecedor no grid, clicando em seguida para gerar o pedido de compra consolidado.
   - **Aba Melhor Preço:** Apresenta por produto o fornecedor com o menor valor individual. Clicar no botão **Gerar Pedidos de Compra** para faturar múltiplos pedidos separados de acordo com os vencedores de cada item.

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:**
  - `Processos > Pedido > Pedidos`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:** `UCPedido`
- **Tabelas envolvidas:**
  - `PEDIDO` — cabeçalho dos pedidos e cotações
  - `PEDIDOITEM` — itens vinculados aos pedidos
  - `PESSOADOC` — cadastro de fornecedores, clientes e comissionados
- **Consultas envolvidas:** [Não informado na documentação]
- **Arquitetura de referência:** [Não informado na documentação]
- **Relatórios Personalizados:** Relatório de Pedido localizado no caminho de diretório `Viasuper > Pedido > PEDIDO`.

## 6. Casos de Falha

### Pedido não é localizado para entrega ou faturamento no PDV
- **Sintoma:** Ao tentar faturar a entrega no PDV, o sistema retorna erro informando que o pedido não foi localizado.
- **Causa:** O tipo de documento do pedido utilizado na Retaguarda está parametrizado incorretamente, com a opção "Envia para PDV" definida como "NÃO".
- **Solução:** Acessar *Configurações > Documentos > Configurações de Pedido*, localizar o documento correspondente e alterar o parâmetro "Envia para PDV" para "SIM".

### Falha ao enviar planilha de cotação por e-mail para os fornecedores
- **Sintoma:** O sistema apresenta erros ou não conclui o envio dos arquivos `.xls` após clicar no botão de envio.
- **Causa:** O cadastro de pessoas dos fornecedores selecionados não possui endereço de e-mail configurado ou contém caracteres inválidos, ou as configurações de SMTP gerais da filial estão inconsistentes.
- **Solução:** Acessar a ficha cadastral do fornecedor no Cadastro de Pessoas, preencher/corrigir o e-mail correspondente e testar a conexão SMTP do ERP.

### Divergências de impostos no faturamento de pedidos antigos
- **Sintoma:** O valor de impostos (ICMS/PIS/COFINS) calculado ao emitir a nota fiscal difere do que constava na visualização do pedido.
- **Causa:** Configurações tributárias gerais do ERP (alíquotas, exceções fiscais ou tabelas tributárias) foram alteradas após a gravação do pedido e antes do seu faturamento.
- **Solução:** Efetuar a rotina de recálculo de tributação no pedido antes da geração da nota, ou processar o recálculo fiscal no rascunho da nota de faturamento antes de realizar a transmissão oficial à Sefaz.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-10 | 1.0 | Criação inicial e estruturação do processo de Pedido e Cotação de Compra no modelo proposto. |
