---
id: PROC-005
titulo: "Gerenciamento de Pedido Centralizado"
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
  - centralizado
  - transferencias
  - compras
  - viasuper
rns_relacionadas:
  - RN-004
  - RN-010
  - RN-007
  - RN-008
  - RN-011
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-11"
data_revisao: "2026-06-11"
---

# Gerenciamento de Pedido Centralizado

## 1. Objetivo

Realizar o planejamento e a emissão centralizada de compras de produtos para toda a rede de supermercados por meio de um setor unificado (matriz ou Centro de Distribuição - CD). O processo visa otimizar a negociação por volume com fornecedores, coordenar a distribuição de estoques entre as lojas (evitando excessos ou rupturas) e automatizar a geração de pedidos de compra e pedidos de transferência interna.

## 2. Pré-condições

- **Configuração Documento Padrão:** Parametrizar previamente os campos *"Conf. Transf Entrada"* e *"Conf. Transf Saída"* na rotina *Configurações » Gerais » Pedido, Análise Compra » Configuração de Documento Padrão para Geração de Pedidos* (necessário para a correta geração de transferências).
- **Mix de Produtos x Comprador:** Configurar a vinculação do usuário comprador aos produtos na rotina *Configurações » Mix de Produtos x Comprador* para habilitar o retorno de dados na sugestão de compras.
- **Mix de Produtos x Estabelecimento:** Configurar as ligações entre produtos e lojas na rotina *Configurações » Mix de Produtos x Estabelecimentos* (exigido para viabilizar as operações do pedido centralizado).
- Cadastro de fornecedores, filiais e produtos atualizado.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina de Pedido Centralizado incluem:

- [[RN-010-compra-centralizada-x-descentralizada]] — **Modalidade de Compra Centralizada:** Define se os pedidos resultantes serão faturados e entregues diretamente no estabelecimento central (Compra Centralizada) ou se serão ramificados e faturados diretamente contra cada filial de destino (Compra Descentralizada).
- RN-0XX-pedidos-de-transferencia-fluxo — **Geração de Pedidos de Transferência:** Ao marcar *"Realizar Pedidos de Transferência"* no fluxo centralizado, o sistema cria automaticamente o pedido de compra contra o CD central, além de pedidos de transferência de saída (do CD) e de entrada (para as lojas filiais).
- [[RN-011-parametrizacao-transferencia]] — **Configurações Padrão de Transferência:** A parametrização tributária e operacional das transferências geradas pelo Pedido Centralizado obedece estritamente às configurações indicadas na rotina *Configuração de Documento Padrão para Geração de Pedidos*.
- RN-0XX-mix-produtos-comprador — **Bloqueio de Itens por Comprador:** A sugestão de compra é filtrada por comprador. Se o produto não estiver vinculado ao comprador ativo no Mix de Produtos, ele é ocultado da tela de sugestão automática.
- RN-0XX-mix-produtos-estabelecimento — **Restrição de Produtos por Filial:** A inclusão manual ou automática de produtos exige que o item esteja habilitado para os estabelecimentos de destino na parametrização do Mix de Produtos por Estabelecimento.
- [[RN-007-sugestao-indice-vendas]] — **Cálculo da Sugestão por Índice de Vendas:** O sistema calcula a sugestão utilizando o histórico temporal de vendas do mês selecionado nos últimos 5 anos e percentuais de volatilidade recentes (Job `AtGiroSazonal` executado no Gerenciador de Tarefas).
- [[RN-008-sugestao-media-vendas]] — **Cálculo da Sugestão por Média de Vendas:** O sistema calcula as sugestões com base na Média Original, Desvio Padrão e Média do cadastro do produto (Job `CalcEstMedVenda` executado no Gerenciador de Tarefas).
- RN-0XX-carregamento-impostos-produtos — **Carregamento Fiscal:** A marcação do checkbox sem título ao lado de *"Realizar Compra Centralizada"* determina se o sistema deve recuperar e exibir as alíquotas de impostos de entrada (ICMS, PIS, COFINS, IPI, Funrural) dos produtos incluídos no grid.
- [[RN-004-rateio-proporcional-itens]] — **Rateio Proporcional nos Itens do Pedido Centralizado:** Valores globais do pedido (como frete, seguro, desconto global e despesas acessórias) são distribuídos proporcionalmente entre os itens com base na participação de cada um no valor total do documento.

## 4. Fluxo do Processo

### 4.1. Configuração e Parâmetros Iniciais do Pedido Centralizado

1. Acessar o menu **Processos > Pedidos > Pedido Centralizado**.
2. Preencher os parâmetros de controle iniciais (checkboxes):
   - **Análise Agrupada Por Produto Mestre:** Organiza a análise com base no agrupamento de produtos mestres configurado.
   - **Realizar Compra Centralizada:** Selecionar para centralizar o faturamento e entrega física no estabelecimento central. Manter desmarcado para fluxo descentralizado.
   - **Carregar Impostos (Checkbox ao lado de Compra Centralizada):** Selecionar para preencher as colunas tributárias dos produtos.
   - **Realizar Pedidos de Transferência:** Habilitar para programar a distribuição interna via transferência (requer *Realizar Compra Centralizada* ativado).
   - **Considerar Somente Estoque Central:** Força o cálculo de sugestões a desconsiderar o estoque das filiais de destino.
3. Preencher os filtros de cabeçalho:
   - **Estab Central:** Informar a filial que centraliza a compra.
   - **Estabelecimentos:** Selecionar um ou mais estabelecimentos de destino para as mercadorias.
   - **Fornecedores:** Fornecedor faturador.
   - **Configuração:** Configuração de pedido de compra padrão.
   - **Observação:** Descrição livre para impressão.
4. Para incluir produtos, utilize o botão **Incluir Produto Manualmente** ou acesse a **Sugestão de Compra** (fluxo 4.2).
5. Salvar o Pedido Centralizado.

---

### 4.2. Cálculo e Execução de Sugestões de Compra

1. Clicar em **Sugestão de Compra** no grid de produtos.
2. Na tela de sugestões, preencher os parâmetros:
   - **Estabelecimentos, Fornecedor e Comprador:** Carregados de acordo com os filtros preenchidos na tela principal do pedido.
   - **Classificação Mercadológica / Curva ABC / Tipo de Giro:** Filtrar Departamento, Setor, Grupo, Família, classificação ABC das mercadorias ou giro (Regular, Irregular ou Sazonal).
   - **Cálculo da Sugestão:** Selecionar se utilizará *Índice de Vendas* (Job Giro Sazonal) ou *Média de Venda Configurada no Pedido* (Job CalcEstMedVenda).
   - **Opções adicionais:** Configurar projeção de estoque em dias, período específico de análise de compras/vendas, saldo de avarias e embalagem configurada.
3. Clicar em **Executar**. O sistema preencherá o grid com os itens sugeridos.
4. No grid inferior de distribuição, o usuário pode revisar e ajustar manualmente as quantidades destinadas a cada filial no campo **Qtde Informada**.
5. Confirmar para exportar os dados sugeridos para a tela principal do Pedido Centralizado.

---

### 4.3. Fluxo 1 — Compra Descentralizada (Não Centralizada)

1. Deixar desmarcado o checkbox **Realizar Compra Centralizada**.
2. Preencher no cabeçalho o Fornecedor, a Configuração de Pedido e as filiais de destino no campo **Estabelecimentos**. O campo *Estab Central* é desconsiderado.
3. Adicionar os produtos e preencher as quantidades específicas de cada loja no grid de distribuição inferior.
4. Salvar o Pedido Centralizado e clicar em **Gerar Pedidos**.
5. Na aba **Pedidos Gerados**, o sistema exibirá os pedidos gerados individualmente para cada filial de destino com o fornecedor informado.
6. A filial de destino realiza o recebimento do pedido na rotina de recepção de pedidos para dar entrada física no estoque e gerar a respectiva nota.

---

### 4.4. Fluxo 2 — Compra Centralizada sem Pedidos de Transferência

1. Marcar o checkbox **Realizar Compra Centralizada** e manter **Realizar Pedidos de Transferência** desmarcado.
2. Preencher no cabeçalho o **Estab Central**, Fornecedor, Configuração e filiais de destino.
3. Adicionar os produtos e a quantidade consolidada de compra.
4. Salvar o documento e clicar em **Gerar Pedidos**.
5. O sistema criará um único pedido de compra faturado contra o estabelecimento central.
6. A filial central realiza o recebimento e o faturamento do pedido na recepção para dar entrada física nos itens em seu CD/loja física.

---

### 4.5. Fluxo 3 — Compra Centralizada com Pedidos de Transferência

1. Marcar os checkboxes **Realizar Compra Centralizada** e **Realizar Pedidos de Transferência**.
2. Preencher no cabeçalho o **Estab Central**, as filiais no campo **Estabelecimentos**, o Fornecedor e a Configuração do pedido de compra.
3. Adicionar os produtos e preencher as quantidades específicas de distribuição no grid.
4. Salvar e clicar em **Gerar Pedidos**. O sistema gerará:
   - Um pedido de compra para o estabelecimento central com o fornecedor externo.
   - Pedidos de transferência de saída (da filial central para as filiais de destino).
   - Pedidos de transferência de entrada (nas filiais de destino com a filial central como emitente).
5. O estabelecimento central recebe e fatura a compra externa.
6. A filial central acessa a rotina de **entrega de pedidos**, localiza os pedidos de transferência gerados para as lojas, seleciona e clica em **Salvar** para gerar as notas de saída de transferência.
7. O emitente transmite e autoriza as notas fiscais na aba **7 - NFe/NFCe**.
8. Cada filial de destino acessa o sistema Retaguarda, abre o menu **Central de Transferências > Notas Pendentes a Receber**, localiza as notas da central e confirma o recebimento para gerar as notas de entrada e movimentar o estoque local das lojas.

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** `Processos » Pedidos » Pedido Centralizado`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:** `ucPedidoCt`
- **Tabelas envolvidas:**
  - `PEDIDO` — pedidos de compra e de transferência gerados pela rotina
  - `NOTACONF` — configurações de documentos de pedidos/transferências
  - `PESSOADOC` — cadastro de fornecedores e filiais
  - `ITEM` — cadastro de produtos, classificações mercadológicas e de giro
  - `PEDIDOCT` - salva o cabeçalho do pedido
  - `PEDIDOCTITE` - informações dos itens dos pedidos centralizados
  - `PEDIDOCTESTAB` - pedidos centralizados realizados em cada estabelecimento
  - `PEDIDOCTITEBKP` - backup dos itens do pedido centralizado
  - `PEDIDOCTESTABBKP` - backup dos pedidos centralizados realizados no estab
- **Jobs / Tarefas Relacionadas:**
  - `AtGiroSazonal` — calcula e atualiza dados do Índice de Vendas.
  - `CalcEstMedVenda` — calcula e atualiza dados de média de vendas e desvio padrão.
- **Consultas envolvidas:** [Não informado na documentação]
- **Arquitetura de referência:** [Não informado na documentação]
- **Relatórios Personalizados:** 

## 6. Casos de Falha

### A sugestão de compras retorna vazia após a execução
- **Sintoma:** O grid de sugestões não exibe nenhum produto após preencher os filtros e clicar em Executar.
- **Causa:** O usuário comprador logado não possui amarração com as mercadorias parametrizada na rotina *Configurações » Mix de Produtos x Comprador*.
- **Solução:** Acessar a parametrização do mix de produtos do comprador e incluir os departamentos/produtos sob sua responsabilidade.

### Bloqueio ou falha de mix de produto por estabelecimento
- **Sintoma:** O sistema impede a inclusão manual de determinado item ou não gera pedidos para filiais específicas.
- **Causa:** O produto não está vinculado aos estabelecimentos de destino na parametrização do menu *Configurações » Mix de Produtos x Estabelecimentos*.
- **Solução:** Revisar as permissões de mix por estabelecimento e liberar os produtos afetados para as respectivas lojas de destino.

### Pedidos de transferência gerados com parametrização de documento incorreta
- **Sintoma:** Os pedidos de transferência interna são criados sem herdar as configurações tributárias ou operacionais adequadas.
- **Causa:** Ausência ou incorreção no preenchimento dos campos "Conf. Transf Entrada" e "Conf. Transf Saída" nas configurações gerais do ERP.
- **Solução:** Acessar *Configurações » Gerais » Pedido, Análise Compra » Configuração de Documento Padrão para Geração de Pedidos* e associar as configurações de transferência corretas.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-11 | 1.0 | Criação inicial e estruturação da documentação de Pedido Centralizado no modelo de processos. |
