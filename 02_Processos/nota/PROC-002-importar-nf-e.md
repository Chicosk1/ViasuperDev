---
id: PROC-002
titulo: "Importação NF-e"
tipo: processo
modulo: "NF-e"
sistema: viasuper
versao_sistema: "1.0.2105"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - nfe
  - importacao-nfe
  - xml
  - viasuper
rns_relacionadas: []
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-11"
data_revisao: "2026-06-11"
---

# Importação NF-e Viasuper

## 1. Objetivo

Facilitar e agilizar o lançamento de notas fiscais de entrada de mercadorias no sistema Viasuper. A partir da chave de acesso do Danfe, o sistema conecta-se à Secretaria da Fazenda (Sefaz), realiza o manifesto de confirmação de operação pelo destinatário (garantindo sua validade jurídica) e efetua o download automático e salvamento do arquivo XML no diretório local parametrizado. O processo realiza também o cadastro automático de fornecedores, vincula itens ao catálogo interno, permite desmembramento de produtos, gerenciamento de embalagens, baixa de pedidos de compra associados e integração com o financeiro e a precificação de venda.

## 2. Pré-condições

- Configuração de Documento de entrada parametrizada no ERP para a recepção das notas.
- Local de Estoque definido para o recebimento físico e atualização de saldos dos produtos.
- Diretório de salvamento de arquivos XML configurado no computador do usuário.
- Cadastro dos produtos previamente realizado no sistema (produtos novos que não constam na base devem ser cadastrados antes do salvamento da importação).

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina de importação de XML incluem:

- RN-00x-carregar-notas-existentes — **Carregar Notas já Existentes:** Se ativado, exibe a nota no grid mas bloqueia sua importação secundária, gerando um status de erro de nota já existente no grid de arquivos carregados.
- RN-00x-baixa-pedido-automatica — **Entregar Pedido após Importação:** Se marcado, ao salvar a nota de entrada com sucesso, o sistema exibe uma mensagem solicitando a confirmação de baixa do pedido de compra vinculado.
- RN-00x-cadastro-atualizacao-fornecedor — **Atualização de Cadastro do Fornecedor:** Se desmarcado ("Não Atualiza Dados do Fornecedor"), o sistema atualiza telefone e endereço do fornecedor de acordo com os dados do XML. Caso o fornecedor não exista no banco de dados, efetua o cadastro automático do mesmo.
- RN-00x-transferencia-entre-filiais — **Transferência de Notas entre Filiais:** Se marcado, permite receber e transferir notas fiscais emitidas pela matriz diretamente para a filial selecionada.
- RN-00x-recalculo-tributario-importacao — **Recálculo Tributário na Importação (ICMS/PIS/COFINS/ICMS-ST):** Quando ativos, os checkboxes de recálculo (Recalcula ICMS, Recalcula PIS, Recalcula COFINS, Recalcula Prod sem valor ICMS-ST) substituem os impostos originais importados com o XML pelas configurações fiscais cadastradas localmente no ERP.
- N-00x-validacao-casas-decimais — **Validações de Casas Decimais (Processamento):** Corrige divergências nos somatórios dos itens causadas por dízimas ou excesso de casas decimais do XML por meio de três opções:
  - *Considerar “Valor total” = “Valor Un Trib” x “Quantidade” do XML* (corrige divergência unitária/quantidade do item).
  - *Considerar “Total a Acertar” = “Valor Total da NF-e” do XML* (corrige divergência entre total calculado e total da NF-e).
  - *Considerar “Total dos Produtos” = ”Valor Total” do grid* (corrige divergência de somatório geral do grid).
- RN-00x-desmembramento-produtos — **Desmembramento de Itens na Importação:** Permite que um produto do XML seja fracionado em múltiplos itens internos. O item original é excluído do grid e os novos produtos herdam as mesmas tributações do registro de origem.
- RN-00x-rateio-custos-importacao — **Rateio de Despesas Acessórias:** Distribui de forma proporcional os valores de frete e despesas adicionais entre os produtos do grid com base em Valor, Peso Bruto ou Quantidade.
- RN-00x-financeiro-pagamento-importacao — **Geração de Contas a Pagar:** Permite realizar o desdobramento financeiro da nota com as duplicatas de pagamento e formas permitidas para o fornecedor, admitindo o uso de múltiplos meios para a mesma NF-e.
- RN-00x-formacao-preco-venda — **Integração com Formação de Preço:** Após concluir a gravação da importação, o sistema exibe uma mensagem direcionando o usuário para a rotina de precificação e formação de preço de venda dos itens importados (sujeito à configuração ativa do ERP).

## 4. Fluxo do Processo

### 4.1. Etapa 1 — Preparação, Manifesto e Carga do XML

1. Acessar o menu **Processos > NF-e > Importação NF-e**.
2. Validar o caminho configurado no campo **Diretório dos Arquivos de XML**.
3. Clicar em **Recuperar XML** para abrir a janela de manifesto de confirmação de operação pelo destinatário, realizar o download do XML da Sefaz e salvá-lo no diretório local.
4. Clicar no botão **Carregar NF's** para ler os arquivos XML da pasta e listá-los no grid *Arquivos Carregados* (*chave de acesso, série, número do documento e emitente*).
5. Selecionar as notas que deseja importar marcando o checkbox na coluna **Importar**.
   - *Nota:* A coluna **Erros** indica falhas estruturais ou de cadastro prévias. A coluna **Mover** remove o arquivo XML do diretório de origem para a pasta de importados ao finalizar.
6. Selecionar a **Configuração de documento** correspondente.
7. Selecionar o **Local de estoque** destinado à entrada dos produtos.
8. Parametrizar as regras de importação e validações de processamento necessárias (conforme Seção 3).
9. Clicar em **Validar NF's** para processar a validação inicial das notas marcadas e abrir a aba **Validação das Informações**.

---

### 4.2. Etapa 2 — Validação, Ajustes Fiscais e Financeiro

1. Na aba **Validação das Informações**, analisar os blocos de controle da tela:
   - **Campo 1 (Status da Nota - Cores da Chave):**
     - *Preto:* Nota sem advertências ou rejeições, elegível para gravação sem ajustes.
     - *Laranja:* Nota possui advertências, permitindo salvar em estado pendente de conferência posterior.
     - *Vermelho:* Nota com rejeições impeditivas (o botão Salvar é bloqueado até a correção).
   - **Campo 2 (Cabeçalho):** Exibe dados gerais (série, número do documento, fornecedor, código de pessoa, emissão). O campo **Data de Entrada** é editável pelo usuário.
   - **Campo 4 (Mensagens de Advertência/Rejeição):** Lista o descritivo detalhado das inconsistências identificadas pelo sistema (ex: produto sem cadastro, CFOP inconsistente, imposto nulo).
2. No **Campo 3 (Itens e Impostos)**, navegar nas abas correspondentes para validação e ajustes fiscais:
   - **Aba Produtos:** Vincular os produtos importados aos códigos de cadastro internos (pressione **F3** para busca rápida). Para desmembrar um produto, clique com o botão direito sobre ele, selecione **Desmembrar Produto** e confirme clicando em **Salvar**.
   - **Aba ICMS:** Ajustar CST, bases e alíquotas de ICMS se necessário, ou marcar o checkbox **Recalcula** para utilizar as regras do ERP.
   - **Abas IPI, PIS e COFINS:** Ajustar CST, bases e alíquotas correspondentes, ou marcar a coluna **Recalcula** para aplicar as parametrizações internas do sistema.
   - **Aba Outros:** Visualizar parâmetros de custos e outras despesas que atualizam o custo final dos itens.
   - **Aba Observações:** Visualizar informações complementares e dados ao fisco importados com o XML.
   - **Aba XML:** Visualizar a estrutura do XML bruto e o protocolo de autorização oficial da Sefaz.
3. No **Campo 5 (Financeiro):** Clicar em **Pagamento** para acessar a tela financeira. Gerar os títulos no contas a pagar selecionando e dividindo os valores nos botões das formas de pagamento disponíveis para o fornecedor.
4. No **Campo 6 (Rateios):** Configurar a distribuição proporcional das despesas:
   - **Rateio de Frete:** Escolher modalidade por Valor, Peso Bruto ou Quantidade.
   - **Rateio de Despesas:** Escolher modalidade por Valor, Peso Bruto ou Quantidade.
5. No **Campo 7 (Totais):** Revisar os totais gerais da nota e incluir valores manuais de CTRC e outras despesas acessórias se necessário.

---

### 4.3. Etapa 3 — Gravação, Log e Formação de Preço

1. Validado todo o conteúdo tributário, vinculações e financeiro da nota fiscal, clicar em **Salvar**.
2. O sistema gerará o log final de importação e abrirá a aba **Log**:
   - Notas salvas com advertências (Laranja) ficam gravadas na situação **Pendente para conferência**.
   - Notas normais são importadas e consolidadas.
3. O ERP exibirá uma mensagem informando que o processo foi concluído com sucesso. Clicar em **OK**.
4. Dependendo das configurações ativas do ERP, o sistema exibirá o diálogo: *"Deseja abrir a formação de preço de venda?"*:
   - Clicando em **Sim**, o sistema abrirá a tela de precificação e formação de margem dos produtos importados.
   - Clicando em **Não**, a rotina é finalizada e o sistema retorna para a tela inicial de arquivos carregados.

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** `Processos » NF-e » Importação NF-e`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:** `uProcImpNfe.pas`
- **Tabelas envolvidas:**
  - `NOTA` — dados de cabeçalho das notas fiscais de entrada
  - `NOTAITEM` — itens vinculados às notas fiscais importadas
  - `PESSOADOC` — cadastro de fornecedores
  - `NOTACONF` — configurações de documentos
  - `PRODUTO` — cadastro de produtos para vinculação e custo
- **Consultas envolvidas:** [Não informado na documentação]
- **Arquitetura de referência:** [Não informado na documentação]

## 6. Casos de Falha

### Mensagem de erro "Nota já existente" no grid
- **Sintoma:** O arquivo XML é carregado, mas a nota fica com status de erro e bloqueia a seleção para importação.
- **Causa:** O checkbox *"Carregar Nota já Existentes"* está marcado e a nota fiscal correspondente já consta cadastrada no banco de dados.
- **Solução:** Verificar se a nota fiscal já foi integrada anteriormente ou revisar as parametrizações de filtros.

### Divergências de arredondamento causadas por dízimas decimais do XML
- **Sintoma:** O sistema apresenta erros no somatório dos itens, valor unitário ou divergência entre o total calculado e o valor da nota fiscal de origem.
- **Causa:** O arquivo XML emitido pelo fornecedor possui excesso de casas decimais em campos de quantidade ou preço.
- **Solução:** Ativar as validações de processamento no bloco de configurações iniciais (*Valor total = Valor Un Trib x Quantidade*, *Total a Acertar = Valor Total da NF-e* ou *Total dos Produtos = Valor Total* do grid).

### Bloqueio no salvamento da nota (Chave de Acesso em Vermelho)
- **Sintoma:** O botão Salvar fica indisponível ou impede a gravação final do processo na aba Validação de Informações.
- **Causa:** Presença de rejeições impeditivas críticas listadas no Campo 4 (como itens do XML sem vínculo ao cadastro de produtos do ERP).
- **Solução:** Resolver a causa da rejeição (realizar o vínculo correto das mercadorias pressionando a tecla F3 ou realizar o cadastro prévio dos itens na base).

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-11 | 1.0.2105 | Atualização, detalhamento completo e reestruturação da rotina na versão do sistema 1.0.2105. |