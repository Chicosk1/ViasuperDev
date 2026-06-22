---
id: PROC-006
titulo: "SyncJet - Importação de Cupons"
tipo: processo
modulo: "pdv"
sistema: viasuper
versao_sistema: "1.0"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - processo
  - pdv
  - syncjet
  - cupom
  - ecommerce
  - integracao
  - viasuper
rns_relacionadas:
  - RN-019
arquiteturas_relacionadas: []
padroes_relacionados: []
jiras_origem: []
data_criacao: "2026-06-18"
data_revisao: "2026-06-18"
---

# SyncJet - Importação de Cupons

## 1. Objetivo

Monitorar, capturar e importar cupons fiscais provenientes dos Pontos de Venda (PDVs) físicos e pedidos de plataformas de e-commerce parceiras para o banco de dados do ERP ViaSuper. O processo é descentralizado em um aplicativo externo (syncJet) para garantir que a carga de leitura de arquivos e comunicação com APIs não interfira na performance ou cause travamentos na retaguarda principal do sistema.

## 2. Pré-condições

- Executável do integrador disponível no diretório padrão: `...\Viasuper\Client\Mercado\SyncJetPDVX.exe`.
- Permissões de leitura e escrita ativas no diretório do executável para manipulação do arquivo de parametrização local.
- Conexões de banco de dados previamente homologadas e nomeadas no ambiente do cliente.
- Usuário do sistema operacional Windows com permissões de leitura e escrita nos diretórios de entrada de arquivos mapeados.

## 3. Regras de Negócio Aplicadas

As validações e regras disponíveis na rotina do syncJet incluem:

- [[RN-019-descentralizacao-importacao-syncjet]] — **Descentralização da Importação:** A captura e integração de dados de vendas fiscais (PDV) e vendas digitais (e-commerce) ocorrem de forma isolada em segundo plano, evitando concorrência de recursos de hardware na retaguarda do ERP.
- RN-037-importacao-manual-controle — **Controle de Modo de Importação:** A execução da importação manual pelo painel visual do syncJet é condicionada à parametrização da tag `ImportacaoManual=1` no arquivo `.conf`. O padrão omitido ou igual a `0` mantém o aplicativo operando estritamente de forma automática e invisível.
- RN-038-redirecionamento-conexao — **Redirecionamento Dinâmico de Banco de Dados:** A tag `Conexao` especifica para qual base de dados os registros serão inseridos, devendo coincidir exatamente com os aliases homologados (Ex: `MEGA` ou `CARPEC`).
- RN-039-sincronizacao-pdv-origem — **Mapeamento de Captura de PDV Físico:** O syncJet lê os arquivos de cupons fiscais diretamente a partir da pasta de rede cadastrada na rotina *Configurações » Sincronização com PDV* do ERP.
- RN-040-integracoes-ecommerce-escopo — **Escopo de Integração de E-commerce:** A parametrização de credenciais de APIs/Tokens e comportamento de vendas online é configurada na retaguarda ViaSuper, podendo ser aplicada em nível global (toda a rede) ou individual por filial (Regras por Estabelecimento).
- RN-041-reprocessamento-arquivos — **Reprocessamento Manual:** Em cenários de contingência ou erros, permite processar manualmente arquivos JSON/txt depositados no diretório do e-commerce através do menu de atalho da plataforma selecionada.

## 4. Fluxo do Processo

### 4.1. Configuração e parametrização do syncJet (.conf e ViaSuper)

1. Acessar o diretório local `...\Viasoft\Client\Mercado\` e abrir o arquivo `SyncJetPDVX.conf` com um editor de texto.
2. Definir os parâmetros de controle local:
   - Configurar `ImportacaoManual=1` se houver necessidade de habilitar a interface gráfica para reprocessamentos manuais.
   - Configurar `Conexao=[Nome_da_Conexao]` com o nome exato da conexão cadastrada no ambiente (ex: `Conexao=MEGA`).
   - Salvar o arquivo.
3. Acessar a retaguarda do ERP **ViaSuper** para parametrizar as origens dos dados:
   - **PDV Físico:** Acessar o menu *Configurações » Sincronização com PDV* e preencher o caminho de rede onde o caixa deposita as vendas.
   - **E-commerce:** Acessar o menu *Configurações » Configurações Gerais » Integrações*, vincular as plataformas parceiras (*iFood/SiteMercado, 9Bits, Vip Commerce*) e definir a abrangência de chaves de API/Tokens (Global ou Por Estabelecimento).
4. Abrir ou reiniciar o executável `SyncJetPDVX.exe` para aplicar as novas configurações de rede e banco de dados.

---

### 4.2. Passo a Passo: Execução e Importação Manual

*(Utilizado para reprocessamento de cupons ou pedidos de e-commerce fora do fluxo automático)*

1. Garantir que a tag `ImportacaoManual=1` esteja ativa no arquivo local `SyncJetPDVX.conf` e abrir o aplicativo `SyncJetPDVX.exe`.
2. No menu lateral esquerdo do syncJet, acessar **Configurações » Importação Manual**.
3. Apontar os caminhos das pastas de rede onde estão os arquivos de cupom/pedido (`.txt` com JSON) de cada integradora correspondente (*9Bits, SiteMercado, Vip, iFood*).
4. Retornar ao menu principal do syncJet.
5. No menu lateral esquerdo, clicar sobre a aba da plataforma desejada (*9Bits, Vip, iFood ou JetPDV*).
6. No painel central, clicar com o botão direito sobre o processo correspondente e selecionar a opção **Cupons** ou **Pedidos** (conforme a operação).
7. O sistema processará os arquivos e exibirá o log e status de importação no painel de *Log de Erros* na parte inferior da tela.

## 5. Componentes Técnicos

- **Linguagem:** Delphi (aplicativo executável externo)
- **Executável principal:** `SyncJetPDVX.exe`
- **Arquivo de configuração:** `SyncJetPDVX.conf`
- **Caminho no menu do ViaSuper:**
  - `Configurações » Sincronização com PDV`
  - `Configurações » Configuração Gerais » Integrações`
- **Plataformas Homologadas:** iFood (SiteMercado), 9Bits, Vip Commerce, JetPDV.
- **Tabelas envolvidas:**
  - `NOTA` — dados de cabeçalho dos cupons fiscais e pedidos integrados
  - `NOTAITEM` — itens vendidos nos cupons integrados
  - `PRODUTO` — cadastro de produtos para validação de saldo e movimentação de estoque
- **Consultas envolvidas:** [Não informado na documentação]
- **Arquitetura de referência:** [Não informado na documentação]

## 6. Casos de Falha

### Mensagem "Diretório de entrada não existe" no Log de Erros
- **Sintoma:** O syncJet exibe alerta no terminal inferior e interrompe a captura automática ou manual de arquivos de cupons.
- **Causa:** O caminho da rede ou pasta local mapeado no ViaSuper (*Sincronização com PDV*) ou no painel de *Importação Manual* está incorreto, inacessível na rede, ou o usuário do Windows não possui privilégios de acesso na pasta.
- **Solução:** Validar a conectividade de rede com a pasta mapeada e conceder permissões de leitura/gravação ao usuário do sistema operacional Windows correspondente.

### Painel ou opções de Importação Manual indisponíveis
- **Sintoma:** A aba ou atalhos para executar a importação manual via botão direito não aparecem na interface do syncJet.
- **Causa:** A tag `ImportacaoManual` no arquivo `SyncJetPDVX.conf` está configurada como `=0` ou não foi declarada.
- **Solução:** Abrir o arquivo `SyncJetPDVX.conf`, declarar a linha `ImportacaoManual=1`, salvar e reiniciar o executável `SyncJetPDVX.exe`.

### Falha de injeção dos cupons no banco de dados do ERP
- **Sintoma:** Os cupons são lidos pelo syncJet, mas não aparecem nas rotinas da retaguarda ViaSuper.
- **Causa:** O alias de conexão configurado na tag `Conexao` do arquivo `.conf` está incorreto ou não corresponde à conexão homologada no banco de dados local.
- **Solução:** Corrigir a parametrização da tag `Conexao` no arquivo `SyncJetPDVX.conf` informando o nome correto (Ex: `MEGA` ou `CARPEC`).

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-18 | 1.0 | Criação inicial e estruturação da documentação da rotina syncJet no modelo de processos. |
