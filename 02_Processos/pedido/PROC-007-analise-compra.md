---
id: PROC-007
titulo: "Análise de Compra"
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
  - compras
  - analise
  - sugestao
  - viasuper
rns_relacionadas:
  - RN-010
  - RN-007
  - RN-008
  - RN-011
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-18"
data_revisao: "2026-06-18"
---

# Análise de Compra

## 1. Objetivo

Na análise de compras é possível gerar pedidos de compra, cotações, transferências e solicitações de produtos, a partir de sugestões geradas pelo sistema com base no estoque atual, histórico de vendas e necessidades da rede. O processo visa garantir o abastecimento sem ruptura ou excesso de estoque.

## 2. Pré-condições

- **Configurações Gerais de Pedidos:** As parametrizações de documento base na rotina *Configurações > Gerais > Processos > Pedidos / Análise de compra* devem estar preenchidas (ex: Conf. Pedido Compra, Conf. Transf. Entrada/Saída, Conf. Cotação).
- **Parâmetros de Análise por Grupo/Usuário:** Acesso e visão de sugestões devem ser habilitados em *Configurações > Usuários > Configuração Grupos / Usuários > Processos > Análise de Compra* (ex: visualizar média de vendas, limites de solicitação).
- **Cadastros:** Pessoas (Fornecedores) e Produtos com estoque mínimo e máximo devidamente configurados.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina de Análise de Compra incluem:

- [[RN-010-compra-centralizada-x-descentralizada]] — **Modalidade de Compra Centralizada:** Se marcado, gera apenas um pedido consolidado para o estabelecimento logado, independentemente de se foram realizadas análises para outros estabelecimentos simultaneamente.
- [[RN-007-sugestao-indice-vendas]] — **Utilizar Índice de Vendas:** A sugestão de compra é gerada baseando-se no comportamento sazonal de vendas do produto.
- [[RN-008-sugestao-media-vendas]] — **Média de Vendas:** Caso marcado, permite visualizar a média de vendas como parâmetro na análise (mesmo para produtos inativos para compra se a opção estiver parametrizada).
- RN-009-previsao-saldo-estoque — **Previsão de Saldo de Estoque:** Calcula a necessidade do produto baseando-se no saldo atual, consumo diário, previsões de entrada/saída futuras. A sugestão considerará a data final informada para essa previsão.
- RN-010-indicadores-visuais-estoque — **Indicadores Visuais no Grid:** Os produtos são sinalizados por cores: Vermelho (estoque negativo), Azul (estoque positivo no estabelecimento logado) e Preto (produtos de outros estabelecimentos).
- [[RN-011-parametrizacao-transferencia]] — **Gerar Pedido de Transferência:** Ao selecionar a quantidade informada para transferência, o sistema obedece às regras e configurações padrão de transferência de saída e entrada.
- RN-042-bloqueio-produtos-inativos — **Não Exibir Produtos Inativos para Compra:** Parâmetro que impede a inclusão e visualização de itens já descontinuados ou bloqueados no catálogo para compra.
- RN-043-analise-com-embalagem — **Conversão por Embalagem:** Se marcado, apresenta as quantidades sugeridas convertidas pela unidade e fator da embalagem vinculada ao fornecedor/produto.
- RN-044-filtro-somente-sugestao — **Somente Produtos com Sugestão:** Quando selecionado, oculta os produtos do mix que não atingiram a quantidade mínima que dispare gatilho de necessidade de compra.

## 4. Fluxo do Processo

### 4.1. Configuração e Filtros de Análise

1. Acessar o menu **Processos > Análise de Compra**.
2. Na aba de filtros, definir os parâmetros base da análise:
   - **Estabelecimentos:** Escolher os estabelecimentos para análise de produtos.
   - **Local de Estoque:** Informar de onde os saldos serão avaliados.
   - **Estabelecimento de Origem para Transferências:** Origem caso a ação seja de transferência interna.
   - **Fornecedor:** Preencher o fornecedor (se não informado, o sistema exigirá na gravação posterior).
3. (Opcional) Refinar a busca utilizando as **Classificações Mercadológicas** (Departamento, Setor, Grupo, Sub-Família) ou Curva ABC.
4. Parametrizar opções de exibição e cálculo nos checkboxes:
   - *Realizar compra centralizada*.
   - *Somente Produtos com Sugestão*.
   - *Previsão de Saldo de Estoque* e *Data Final para Previsão de Saldo*.
   - *Utilizar Índice de Vendas* ou *Análise de Saldos/Valores c/ Embalagem*.
5. (Opcional) Definir **Usuário Comprador** para restringir a análise aos itens do mix daquele responsável.
6. Clicar em **Avançar/Executar** para gerar o grid da análise.

---

### 4.2. Análise e Visualização do Grid

1. Analisar os produtos carregados no painel principal:
   - As linhas serão coloridas conforme a regra visual (*RN-010*).
   - O grid apresenta dados essenciais: Estoque atual, mínimo e máximo, saldo de avarias, consumo diário, consumo mensal e durabilidade em dias do saldo atual.
   - A aba "Pedidos" exibe o que há a receber e a enviar para outras filiais.
2. Conferir as **Sugestões:** A coluna de "Sugestão" mostra a quantidade sugerida pelo sistema com base na matemática de saldo vs. consumo e prazos.
3. Para consultar os Detalhes do Produto, clicar no botão de seta de expansão ao lado do código do produto.
4. Clicar com o botão direito no grid permite:
   - Associar produtos ao fornecedor.
   - Ajustar colunas.
   - Atualizar a quantidade informada para ser igual à sugestão ("Atualizar Qtde Info. = Sugestão") ou zerar a quantidade.

---

### 4.3. Geração das Ações de Compra ou Transferência

1. No campo **Quantidade Informada (Qtde Info.)**, inserir a quantidade final desejada.
2. Marcar o checkbox de **Gerar** na respectiva coluna da ação pretendida (ex: *Pedido* ou *Transferência* ou *Cotação*).
3. Após definir todos os itens e quantidades, clicar em **Próximo**.
4. Confirmar o fornecedor na tela seguinte e avançar.
5. Na aba **Previsão de Entrega**, informar parcelamento de entregas caso haja programação, e clicar em **Gerar Previsões**.
6. Avançar para a tela de **Previsão de Pagamento**, gerar o parcelamento ou as datas de vencimento conforme a negociação com o fornecedor e clicar em **Gerar Previsões**.
7. Clicar em **Próximo** para acessar a tela de finalização.
8. Revisar os números e clicar em **Salvar (Salvar - Gerar Pedidos)** para que o sistema efetive a gravação dos documentos e pedidos de compra/transferência no banco de dados.

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** `Processos > Análise de Compra`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:** [Não informado]
- **Tabelas envolvidas:** 
  - `PEDIDO` (geração de ordens)
  - `ITEM` / `PRODUTO` (estoque e mix)
  - `PESSOADOC` (fornecedor)
  - `NOTACONF` (configuração do documento de transferência e pedido)
- **Consultas envolvidas:** [Não informado]
- **Arquitetura de referência:** [Não informado]

## 6. Casos de Falha

### Erro na gravação: Falta de Fornecedor
- **Sintoma:** O sistema não permite salvar a análise e exibe mensagem de atenção.
- **Causa:** O usuário tentou gerar um pedido de compra, porém o filtro "Fornecedor" não foi preenchido na tela inicial nem na tela de transição de fechamento.
- **Solução:** Voltar à tela anterior e preencher o código ou nome do fornecedor correspondente.

### Produtos não aparecem no grid (Grid Vazio)
- **Sintoma:** Ao clicar em executar/avançar, o grid retorna zerado.
- **Causa:** Conflitos de filtros. O usuário pode ter marcado "Somente Produtos com Sugestão" e os itens selecionados não atingiram o ponto de reposição, ou os filtros mercadológicos foram muito restritivos. Também pode ocorrer se o "Usuário Comprador" não tiver mix amarrado.
- **Solução:** Desmarcar filtros avançados e rodar a busca novamente, ou verificar o amarrilho de produtos ao cadastro do usuário logado.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-18 | 1.0.2105 | Criação inicial e documentação da rotina de Análise de Compra. |
