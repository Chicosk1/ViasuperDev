---
id: RN-001
titulo: "Filtro de intervalo de datas obrigatório em buscas e consultas do ERP"
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
  - filtro
  - performance
  - consulta
processos_relacionados:
  - PROC-001
  - PROC-002
  - PROC-003
  - PROC-004
  - PROC-008
padroes_relacionados:
  - PT-002
data_criacao: "2026-05-21"
data_revisao: "2026-06-19"
---

# Filtro de intervalo de datas obrigatório em buscas e consultas do ERP

## 1. Definição

Em qualquer rotina do ERP que realize buscas ou consultas sobre grandes volumes de dados históricos (duplicatas, notas fiscais, pedidos, movimentações de estoque, cupons, etc.), a execução da consulta só é permitida se ao menos **um filtro de intervalo de datas** estiver preenchido. O sistema deve bloquear consultas abertas sem restrição temporal para proteger a performance do banco de dados e evitar retorno de dados irrelevantes ou obsoletos.

Esta regra se aplica a todas as telas de filtro/pesquisa do ERP que operam sobre tabelas transacionais com histórico acumulado ao longo do tempo.

## 2. Contexto

Bases de dados de ERP de varejo acumulam anos de histórico transacional (notas fiscais, pedidos, cupons, movimentações). Uma consulta sem restrição de data pode retornar milhões de registros, causando lentidão extrema no banco de dados, travamento da tela para o usuário e potencial impacto para outros usuários conectados ao sistema. Além do problema de performance, resultados sem filtro temporal tornam a análise impraticável e aumentam o risco de o operador tomar ações equivocadas sobre registros antigos já encerrados.

## 3. Condição (Se / Então)

- **Se:** o usuário clicar em **Executar / Pesquisar / OK** em uma tela de filtro sem preencher nenhum campo de intervalo de datas (Ex: Data de Emissão, Data de Baixa, Data do Pedido, Data de Movimento);
- **Então:**
  1. O sistema **bloqueia** a execução da consulta.
  2. Exibe uma mensagem de validação clara indicando que ao menos um intervalo de datas deve ser informado.
  3. O cursor é posicionado no primeiro campo de data disponível para facilitar o preenchimento.
- **Senão (filtro de data informado):** a busca é executada normalmente, aplicando todos os filtros informados (data + demais parâmetros opcionais como fornecedor, produto, situação, etc.).

## 4. Exemplos

### Válido — Consulta de notas fiscais com data de emissão

Usuário acessa *Processos > Nota Fiscal* e preenche apenas **Data de Emissão de** `01/06/2026` **até** `30/06/2026`. Clica em executar. A busca retorna as notas do período.

### Válido — Consulta de duplicatas com data de baixa

Usuário acessa *Gerar Notas de Crédito/Débito* e preenche apenas **Data de Baixa de** `01/05/2026` **até** `31/05/2026`. A busca retorna somente as duplicatas baixadas no mês.

### Válido — Consulta de pedidos com múltiplos filtros

Usuário informa **Data do Pedido** + **Fornecedor**. Ambos os filtros são aplicados conjuntamente.

### Inválido — Consulta sem data

Usuário acessa *Processos > Nota Fiscal* e deixa todos os campos de data em branco. Clica em Executar. O sistema bloqueia e exibe: *"Informe ao menos um intervalo de datas para realizar a consulta."*

## 5. Exceções

- Telas de **consulta de cadastro** (ex: Cadastro de Produtos, Pessoas, NCM) não possuem natureza temporal e estão isentas desta regra.
- Consultas executadas por **relatórios agendados** ou **jobs automáticos** podem ter datas definidas programaticamente, sem intervenção do usuário.
- Telas de **monitoramento em tempo real** (ex: monitor de PDV) operam sobre dados do dia corrente e estão implicitamente filtradas pela data atual — não exigem preenchimento manual.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — regra de validação de interface aplicada universalmente nas telas de filtro com dados transacionais históricos.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.1 | Generalização da regra para abranger todas as telas de filtro/consulta do ERP com dados históricos, não apenas a rotina de Notas de Crédito/Débito. Adição de exemplos de múltiplas rotinas. |
| 2026-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critério 3.5) |
