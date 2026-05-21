---
id: RN-001
titulo: "Filtro de intervalo de datas obrigatório na busca de duplicatas"
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
  - validacao
  - duplicatas
processos_relacionados:
  - PROC-001
padroes_relacionados: []
data_criacao: "2025-05-21"
data_revisao: "2025-05-21"
---

# Filtro de intervalo de datas obrigatório na busca de duplicatas

## 1. Definição

Na rotina Gerar Notas de Crédito/Débito, a execução da busca de duplicatas só é permitida se ao menos um filtro de intervalo de datas (Data de Emissão ou Data de Baixa) estiver preenchido.

## 2. Contexto

Sem restrição de data, a consulta retornaria o histórico completo de baixas de duplicatas do sistema, gerando risco de performance e de geração acidental de notas fiscais sobre operações antigas já encerradas.

## 3. Condição (Se / Então)

- **Se:** o usuário clicar em Executar sem preencher nenhum dos campos Data de Emissão (de/até) e Data de Baixa (de/até).
- **Então:** o sistema deve bloquear a execução e exibir mensagem de validação solicitando o preenchimento de ao menos um intervalo de datas.
- **Senão:** a busca é executada normalmente com os filtros informados.

## 4. Exemplos

### Válido
Usuário preenche apenas Data de Baixa de `01/05/2025` até `31/05/2025` e clica em Executar. A busca é realizada.

### Válido
Usuário preenche Data de Emissão e Data de Baixa simultaneamente. A busca é realizada com ambos os filtros aplicados.

### Inválido
Usuário deixa todos os campos de data em branco e clica em Executar. O sistema bloqueia e exibe mensagem de validação.

## 5. Exceções

Nenhuma exceção prevista.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — regra de validação de interface.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2025-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critério 3.5) |
