---
id: RN-011
titulo: "Parametrização e Herança de Configurações em Pedidos de Transferência"
tipo: regra-negocio
modulo: "pedido"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - pedido
  - transferencia
  - configuracao
  - fiscal
  - centralizado
processos_relacionados:
  - PROC-005
  - PROC-007
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Parametrização e Herança de Configurações em Pedidos de Transferência

## 1. Definição

Quando o ERP gera pedidos de transferência de forma automática (a partir do Pedido Centralizado ou da Análise de Compra), as configurações tributárias, operacionais e logísticas aplicadas a esses documentos devem ser herdadas **exclusivamente** dos parâmetros definidos na rotina **"Configuração de Documento Padrão para Geração de Pedidos"**. O sistema não permite que cada pedido de transferência seja configurado individualmente durante o processo de geração em lote.

Esta regra se aplica a qualquer rotina que gere pedidos de transferência interna de forma automatizada no ERP.

## 2. Contexto

Em redes com múltiplas filiais, o processo de transferência interna de mercadorias (do Centro de Distribuição para as lojas) envolve obrigações fiscais específicas: emissão de nota fiscal de transferência com CFOP correto, tributação de ICMS em transferências interestaduais ou isenção em intraestaduais, etc. Para garantir a padronização e a conformidade fiscal de todos os documentos gerados em lote, o ERP centraliza esses parâmetros em uma configuração única que é herdada automaticamente.

## 3. Condição (Se / Então)

- **Se:** o sistema vai gerar um ou mais pedidos de transferência interna de forma automática (ex: pelo Pedido Centralizado com opção "Realizar Pedidos de Transferência" marcada);
- **Então:**
  1. O sistema consulta os campos *"Conf. Transf. Entrada"* e *"Conf. Transf. Saída"* configurados em *Configurações > Gerais > Processos > Pedidos / Análise de Compra > Configuração de Documento Padrão para Geração de Pedidos*.
  2. Aplica a configuração de **Saída** ao pedido emitido pelo estabelecimento remetente (CD/Matriz).
  3. Aplica a configuração de **Entrada** ao pedido emitido pelo estabelecimento destinatário (Filial).
  4. Os impostos (ICMS, PIS, COFINS), CFOP, série e demais campos fiscais são preenchidos automaticamente conforme essas configurações.
  5. **Não** é possível alterar individualmente a configuração de cada pedido de transferência durante o processo de geração em lote — qualquer ajuste deve ser feito previamente na configuração padrão.

## 4. Exemplos

### Válido — Geração de transferências com configuração correta

Pedido Centralizado com 3 filiais:
- Conf. Transf. Saída: "NF-Transferência Saída – CFOP 5152 (intraestadual)"
- Conf. Transf. Entrada: "NF-Transferência Entrada – CFOP 1152 (intraestadual)"

Resultado: 3 pedidos de saída do CD e 3 pedidos de entrada nas filiais, todos com CFOP e tributação corretos herdados da configuração.

### Inválido

Tentar configurar CFOP diferente para cada filial durante a geração do lote. O sistema não oferece essa granularidade no processo automatizado — a configuração é global para todos os documentos do lote.

### Caso de Erro Comum

Se os campos "Conf. Transf. Entrada" ou "Conf. Transf. Saída" estiverem em branco na configuração padrão, o sistema pode:
- Gerar os pedidos de transferência sem configuração de documento (resultando em erro de validação fiscal).
- Bloquear a geração e exibir mensagem de atenção solicitando a parametrização.

## 5. Exceções

- Pedidos de transferência lançados **manualmente** (via *Processos > Pedido > Pedidos*, clicando em "Abrir Vazio") permitem a seleção individual da configuração do documento.
- Em alguns casos específicos de negociação entre filiais, pode ser necessária uma configuração diferente (ex: transferência interestadual). Nesses casos, o pedido deve ser lançado manualmente ou a configuração padrão deve ser temporariamente ajustada antes da geração em lote.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Conf. Transf. Saída | Configurações > Gerais > Processos > Pedidos > Conf. Documento Padrão | Configuração aplicada ao pedido de saída (CD/Remetente) |
| Conf. Transf. Entrada | Configurações > Gerais > Processos > Pedidos > Conf. Documento Padrão | Configuração aplicada ao pedido de entrada (Filial/Destinatário) |
| CFOP | Herdado da configuração do documento | Define a natureza fiscal da transferência |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Pedido Centralizado e Análise de Compra |
