---
id: PROC-003
titulo: "Gerenciamento de Nota Fiscal"
tipo: processo
modulo: "nota"
sistema: viasuper
versao_sistema: "1.0.2105"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - nota
  - nfe
  - nfse
  - reinf
  - viasuper
rns_relacionadas: []
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-10"
data_revisao: "2026-06-10"
---

# Gerenciamento de Nota Fiscal

## 1. Objetivo

Permitir o gerenciamento completo de notas fiscais de entrada e saída, incluindo emissão, cancelamento, cartas de correção, impressão do Documento Auxiliar da Nota Fiscal Eletrônica (Danfe/Nfse) e geração de notas a partir de outros documentos referenciados no sistema. Adicionalmente, gerencia a parametrização e geração automática do registro R-4020 (REINF) para notas fiscais de serviços (NFS-e).

## 2. Pré-condições

- Configurações de Documento
- Cadastro de Pessoas
- Cadastro de Produtos/Serviços
- Tributação de Serviço
- Instalar o certificado digital no sistema.
- Parametrizações tributárias e cadastrais do emitente e destinatários devidamente preenchidas.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina incluem:

- RN-00x-formas-pagamento — **Formas de Pagamento Permitidas:** O pagamento da nota pode ser registrado através de 6 formas: Dinheiro (à vista), Cheque (em cheque), Cartão (crédito/débito), Duplicata/Boleto (a prazo), Conta Pessoal (saldo liberado ao portador) e Outros (convênios da empresa).
- RN-00x-rateio-frete — **Critérios de Rateio de Frete:** O valor de frete e despesas pode ser distribuído proporcionalmente com base em três modalidades de cálculo definidas na aba Detalhes: por Valor da mercadoria, por Quantidade de itens ou por Peso Bruto.
- RN-00x-bonificacao-produtos — **Tratamento de Bonificações:** Se a flag Bonificação estiver marcada, o valor do item correspondente é deduzido do total final da nota fiscal, e sua tributação seguirá o cadastro específico de bonificações definido na Configuração de Documento.
- RN-00x-numeracao-e-serie — **Sequenciamento de Série e Numeração:** A série é associada de forma automática à configuração do documento. O número oficial do documento permanece em `0` (rascunho) e só é preenchido definitivamente após a autorização da nota junto à Sefaz.
- RN-00x-emissao-a-partir-de — **Notas Referenciadas (A partir de):** Para emitir uma nota referenciando outros documentos (como devoluções ou vendas de cupom fiscal), o documento de origem correspondente já deve estar previamente lançado e ativo no Viasuper.
- RN-00x-nfse-parametrizacao — **Requisitos para Emissão de Nota de Serviço (NFS-e):** O documento de serviço exige espécie `NFSE`, operação de entrada e os parâmetros `Movimenta Financeiro = Sim` e `Tipo Emissão = Terceiros` ativados.
- RN-00x-recalculo-tributacao — **Recálculo de Tributação:** O sistema permite recalcular e atualizar os impostos da nota fiscal para fins de ajuste até o momento da sua transmissão oficial para a Sefaz.

## 4. Fluxo do Processo

### 4.1. Consulta de Nota Fiscal

1. Acessar o menu **Processos > Nota > Nota Fiscal**.
2. No campo **Selecione a Consulta**, clicar na seta lateral e selecionar **Nota**.
3. (Opcional) Informar filtros para refinar a busca: *situação, data emissão, data entrada/saída, código/nome da pessoa, configuração de documento, código da nota ou número do documento*. Caso não deseje aplicar filtros, mantenha o valor `(Ignorar)` selecionado.
4. Clicar em **OK** para carregar os resultados.
5. Para detalhar uma nota fiscal ou visualizar suas abas internas, efetuar um duplo clique sobre a linha correspondente no grid de consulta.

---

### 4.2. Gerando e Emitindo uma Nota Fiscal (Venda de Mercadoria)

1. Na janela **Consulta: Nota**, clicar em **Incluir** (ou usar o atalho **Ctrl + Ins**).
2. No campo **Configuração**, informar a parametrização de documento (atalho **F3** abre a pesquisa. Ex: *"201 – Venda de mercadoria adquirida ou recebida de terceiros"*).
3. Informar as datas de **Emissão** e **Entrada/Saída**.
4. No campo **Cliente**, pesquisar pelo nome (atalho **F3**), código interno ou informar CPF/CNPJ.
5. No grid de produtos, clicar em **Incluir um novo item** (ou usar o atalho **Ctrl + N**) para abrir a janela de inclusão de produto:
    - Buscar o produto por código, código de barras ou nome.
    - Opcionalmente, selecionar Embalagem e Local de Estoque.
    - Informar a **Quantidade** e o **Valor Unitário** (ou informar o valor total para que o sistema calcule o unitário proporcionalmente).
    - Informar descontos em valor absoluto ou percentual, se aplicável.
    - Marcar a flag **Bonificação** se o item for bonificado (isso desconta o valor do item no total da nota e aplica regras fiscais dedicadas).
    - Para manter a tela aberta e lançar mais produtos sequencialmente, marcar a flag **Continuar incluindo**.
    - Clicar em **Salvar** na janela de inclusão de itens.
6. (Opcional) Conferir as informações adicionais nas seguintes abas:
    - **Aba 2-Detalhes:** Conferir dados de entrega do cadastro de pessoa e definir a base de cálculo do frete (Valor, Quantidade ou Peso Bruto).
    - **Aba 3-Transporte:** Cadastrar dados de transportadora, placa do veículo, tipo de frete e peso bruto/líquido.
    - **Aba 4-Impostos:** Validar bases de cálculo, alíquotas e valores de ICMS, ICMS ST, PIS, COFINS, IPI Importação e Ajustes Fiscais.
    - **Aba 5-Mensagens:** Informar dados e observações destinadas ao Fisco ou de cunho comercial.
    - **Aba 6-Impostos Retidos:** Validar as retenções geradas.
    - **Aba 7-Nfe/NFCe:** Validar chaves de acesso, dados da NF-e e documentos referenciados.
7. Clicar no botão **Pagamento** no cabeçalho e selecionar o meio correspondente (Dinheiro, Cheque, Cartão, Duplicata/Boleto, Conta Pessoal ou Outros), digitando o respectivo valor. Clicar em **OK** para confirmar.
8. Salvar o documento clicando em **Salvar** (ou atalho **Ctrl + S**).
9. Clicar em **Transmitir**. O sistema gerará a chave de acesso e transmitirá o arquivo XML para validação e autorização da Sefaz.
10. O sistema enviará o Danfe e o XML por e-mail para o cliente (caso esteja devidamente configurado no cadastro de pessoas).
11. Responder se deseja imprimir o Danfe na mensagem exibida em tela. Caso clique em "Não", a impressão ou reenvio poderão ser executados posteriormente no menu *Gera xml / Imprime Danfe*.

---

### 4.3. Gerando e Emitindo com Importação "A partir de" (Cupom Fiscal)

1. Na tela de **Nota**, clicar em **Incluir**.
2. Selecionar uma configuração destinada a "Venda em Decorrência de Cupom Fiscal" (ou outra finalidade referenciada).
3. Preencher o campo **Cliente** e teclar **Enter** para abrir a tela de vinculação de documentos de origem.
4. Utilizar os filtros disponíveis (Configurações de documentos, Pessoa, Produto, Usuário, Documento dos últimos dias, Local de estoque, ID Notas, Número documento ou PDV) para localizar os registros de cupom fiscal.
5. Clicar no botão **Executar**.
6. No grid **Documentos**, marcar a coluna **Gerar** para os cupons desejados.
7. No grid **Itens dos Documentos**, marcar a coluna **Gerar** para selecionar as mercadorias, podendo ajustar o saldo na coluna **Qtd à Ref.** (limitado ao saldo disponível).
8. Salvar a tela de importação de documentos (atalho **Ctrl + S**). Os itens selecionados e os cupons fiscais referenciados (na aba **7-Nfe/NFCe**) serão integrados à nota automaticamente.
9. Finalizar salvando a nota fiscal principal e clicando em **Transmitir**.

---

### 4.4. Emissão de Notas Fiscais de Serviço (NFSE) e Exportação do R-4020

1. Acessar a rotina de notas e clicar em **Incluir**.
2. Preencher a configuração de documento destinada à NFSE e selecionar o prestador do serviço (PJ).
3. Incluir o item de serviço e preencher os dados de quantidade, preço e garantir a inclusão da Natureza de Rendimento.
4. Acessar a aba **Pagamentos**, escolher a modalidade **Boletos** e clicar em **Executar** para provisionar a duplicata a pagar. Clicar em **Salvar** para gravar.
5. Verificar os tributos retidos calculados na aba **6 - Impostos Retidos**.

## 5. Componentes Técnicos

- **Linguagem:** Delphi
- **Caminho no menu:** 
  - `Processos > Nota > Nota Fiscal`
  - `Configurações > Documentos > Configuração de Documento`
- **Disponibilidade:** Viasuper Padrão e Viasuper Titan
- **Unit principal:**  `UCNota`
- **Tabelas envolvidas:** 
  - `NOTACONF` — parametrização do documento de nota fiscal
  - `PESSOADOC` — dados cadastrais de clientes/fornecedores
  - `DUPPAG` — duplicatas geradas a pagar
  - `ITEMPRVDA` — gerenciamento fiscal e tributário de itens
  - `NOTA` - dados das notas no geral
  - `NOTAITEM` - dado dos itens da nota
  - `NOTAITEMIMPOSTOIVA` - dado dos impostos referente aos itens das notas

- **Consultas envolvidas:** [Não informado na documentação]
- **Arquitetura de referência:** [Não informado na documentação]

## 6. Casos de Falha

### E-mail com Danfe/XML não enviado ao cliente
- **Sintoma:** O processo de transmissão é concluído com sucesso, mas o e-mail não chega ao cliente.
- **Causa:** O e-mail do destinatário está em branco ou cadastrado incorretamente em seu cadastro de pessoa.
- **Solução:** Acessar o Cadastro de Pessoas, corrigir/preencher o e-mail do cliente e retransmitir/enviar pelo menu de reenvio de Danfe.

### Danfe não foi impresso após autorização da Sefaz
- **Sintoma:** Transmissão autorizada sem erros, mas não houve impressão física.
- **Causa:** O usuário respondeu "Não" ao prompt de confirmação de impressão.
- **Solução:** Acessar a rotina "Gera xml / Imprime Danfe" para realizar a consulta da nota emitida e imprimir o documento fiscal.

### Valores retidos informados na coluna de Depósito Judicial incorretamente
- **Sintoma:** Os valores de base e retenções estão constando como depósitos judiciais no Fiscal 3.0.
- **Causa:** Prestador de serviços possui um processo cadastrado e marcado como tipo judicial no Viasuper.
- **Solução:** Avaliar o cadastro do prestador de serviços e alterar o tipo de processo para administrativo se necessário.

### Configuração de documento inválida ou incompatível
- **Sintoma:** O sistema impede a gravação da nota fiscal, apresenta erros de CFOP ou gera inconsistências tributárias críticas.
- **Causa:** O usuário utilizou uma configuração de documento incorreta para a operação (ex: tentar usar configuração de entrada para uma nota de venda) ou com parâmetros mal configurados.
- **Solução:** Selecionar a configuração de documento correta compatível com a operação ou ajustar a parametrização em *Configurações > Documentos > Configuração de Documento*.

### Itens sem tributação cadastrada no sistema
- **Sintoma:** Ao incluir o produto ou tentar salvar a nota, o sistema alerta sobre a falta de tributação/imposto, impede o processamento ou deixa os valores de impostos zerados.
- **Causa:** O produto adicionado não possui uma regra de tributação vinculada à sua classe/CFOP no módulo fiscal para a operação executada.
- **Solução:** Acessar o cadastro do produto ou as tabelas de tributação e configurar as regras de ICMS/PIS/COFINS antes de prosseguir com a emissão da nota.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-10 | 1.0 | Criação inicial e reestruturação da documentação de Nota Fiscal (origem: v1.0.2105). |
