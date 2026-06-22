---
id: RN-019
titulo: "Descentralização do Processo de Importação via SyncJet"
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
  - syncjet
  - integracao
  - cupom-fiscal
  - ecommerce
  - importacao
processos_relacionados:
  - PROC-006
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Descentralização do Processo de Importação via SyncJet

## 1. Definição

O processo de captura e importação de cupons fiscais (PDV físico) e pedidos de e-commerce para o banco de dados do ERP deve ocorrer de forma **descentralizada**, executada pelo aplicativo externo **SyncJet** (`SyncJetPDVX.exe`), e não diretamente pelo processo principal da Retaguarda. Esta separação garante que a carga de leitura de arquivos, comunicação com APIs externas e processamento de dados não interfira na responsividade e performance da Retaguarda ViaSuper para os usuários operacionais.

Esta regra se aplica a qualquer fluxo de importação em massa de dados de venda (cupons de PDV físico ou pedidos de plataformas de e-commerce) para o ERP.

## 2. Contexto

Em supermercados com alto volume de transações, o processamento de centenas ou milhares de cupons fiscais e pedidos de e-commerce simultaneamente pode consumir recursos significativos de CPU, memória e I/O de disco. Se esse processamento ocorresse dentro do processo principal da Retaguarda, causaria lentidão e travamentos para os usuários que realizam lançamentos de notas, pedidos e consultas. A solução arquitetural do SyncJet isola essa carga em um processo separado, rodando em segundo plano ou em uma máquina dedicada.

## 3. Condição (Se / Então)

**Importação de Cupons Fiscais (PDV Físico):**
- **Se:** novos arquivos de cupons fiscais (formato XML, TXT ou proprietário) aparecem no diretório monitorado pelo SyncJet;
- **Então:**
  1. O SyncJet detecta os arquivos no diretório de origem configurado (caminho da pasta de rede do PDV).
  2. Processa cada arquivo, extrai os dados dos cupons (itens, valores, impostos, forma de pagamento).
  3. Insere os registros no banco de dados do ERP (tabelas de cupom/movimento de caixa), usando a conexão de banco definida na tag `Conexao` do arquivo `.conf`.
  4. Move ou marca os arquivos processados para evitar reprocessamento duplicado.
  5. O processo principal da Retaguarda **não** participa diretamente dessa leitura de arquivos.

## 4. Exemplos

### Válido — Loja com 5 caixas e alto volume de vendas

Loja processa 2.000 cupons/dia entre os 5 PDVs. O SyncJet roda continuamente em segundo plano, importando os cupons em lotes a cada X minutos. Os operadores da Retaguarda não percebem qualquer lentidão durante esse processo.

### Inválido

Configurar a Retaguarda ViaSuper para fazer a leitura direta dos arquivos de cupom do PDV dentro do processo principal. Isso causaria bloqueios de I/O e lentidão para todos os usuários conectados ao ERP durante os picos de processamento.

## 5. Exceções

- Em ambientes de baixo volume (lojas pequenas, < 200 cupons/dia), o processamento pode ser tolerado em modo menos frequente, com intervalos maiores entre as execuções do SyncJet.
- O SyncJet pode operar em **modo manual** (com interface visual) para permitir reprocessamento de arquivos com erro ou importação pontual, desde que a tag `ImportacaoManual=1` esteja configurada no `.conf` — conforme RN-037-importacao-manual-controle.
- Em caso de falha na conexão com o banco de dados, o SyncJet deve armazenar os dados em fila local e retentar a inserção quando a conexão for restabelecida.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| `Conexao` | Arquivo `.conf` do SyncJet | Define o alias do banco de dados de destino (ex: MEGA, CARPEC) |
| Diretório de Monitoramento | Configurações > Sincronização com PDV | Caminho da pasta de rede com os arquivos de cupom |
| Credenciais de API E-commerce | Configurações > Integrações > E-commerce | Token e URL de acesso à plataforma de vendas online |
| `ImportacaoManual` | Arquivo `.conf` do SyncJet | Habilita (1) ou desabilita (0) o modo de importação manual com interface |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base no PDF do SyncJet - Importação de Cupons |
