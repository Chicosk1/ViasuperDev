---
id: RN-006
titulo: "Configuração de documento deve ter finalidade Nota de Crédito ou Nota de Débito"
tipo: regra-negocio
modulo: "fiscal"
status: ativo
criticidade: media
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - fiscal
  - configuracao-documento
  - validacao
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Configuração de documento deve ter finalidade Nota de Crédito ou Nota de Débito

## 1. Definição

Na rotina Gerar Notas de Crédito/Débito, o campo Configuração de Documento só aceita e exibe configurações cuja finalidade de emissão seja `5 - Nota de Crédito` ou `6 - Nota de Débito`. O preenchimento é obrigatório para acionar a geração.

## 2. Contexto

A configuração de documento define os parâmetros fiscais da NF-e gerada (série, CFOP, modelo, etc.). Usar uma configuração com finalidade incorreta geraria notas com tipo fiscal errado, causando rejeição na Sefaz e inconsistência contábil.

## 3. Condição (Se / Então)

### 3.1 Finalidade da configuração de documento diferente de 5 ou 6 
- **Se:** o usuário tentar selecionar uma configuração de documento com finalidade diferente de `5` ou `6` no campo Conf. de Documento.
- **Então:** a configuração não deve ser exibida nem aceita no campo.

### 3.2 Gerar Notas sem preencher o campo configuração de documento
- **Se:** o usuário clicar em Gerar Notas sem preencher o campo Conf. de Documento.
- **Então:** o sistema deve bloquear e exibir mensagem de validação obrigando o preenchimento.

## 4. Exemplos

### Válido
Usuário seleciona configuração com finalidade `5 - Nota de Crédito`. Geração prossegue.

### Válido
Usuário seleciona configuração com finalidade `6 - Nota de Débito`. Geração prossegue.

### Inválido
Usuário tenta selecionar configuração com finalidade `1 - Normal`. A configuração não deve aparecer na lista de opções.

### Inválido
Usuário clica em Gerar Notas com campo Conf. de Documento em branco. Sistema bloqueia com mensagem de validação.

## 5. Exceções

Nenhuma exceção prevista.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Valor esperado | Efeito |
|---|---|---|
| `FINALIDADEEMISSAO` | `5` ou `6` | Determina se a configuração é exibida e aceita no campo |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2025-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021) (critérios 3.3 e 3.8) |
