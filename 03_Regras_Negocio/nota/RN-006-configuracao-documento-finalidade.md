---
id: RN-006
titulo: "Direcionamento, Permissões e Impacto nos Saldos das Configurações de Documento"
tipo: regra-negocio
modulo: "fiscal"
status: ativo
criticidade: alta
imutavel: false
versao_template: "1.0"
contexto_llm: alto
tags:
  - regra-negocio
  - fiscal
  - configuracao-documento
  - estoque
  - permissao
  - operacao
processos_relacionados:
  - PROC-001
  - PROC-002
  - PROC-003
  - PROC-004
  - PROC-008
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-06-22"
---

# Direcionamento, Permissões e Impacto nos Saldos das Configurações de Documento

## 1. Definição

As **Configurações de Documento** são o núcleo paramétrico que direciona todas as rotinas de emissão de notas fiscais e servem de matriz para a criação das Configurações de Pedido no sistema. O papel fundamental dessas configurações não é apenas definir a finalidade fiscal, mas sim determinar **como a operação afetará os saldos** (físicos e financeiros) e qual é a **natureza da transação** (compra, venda, ajuste de estoque, devolução, etc.).

Além disso, por segurança operacional, a listagem de configurações disponíveis em qualquer rotina de nota ou pedido obedece a um critério rígido de visibilidade: a configuração só é exibida e pode ser selecionada caso tenha sido **explicitamente desbloqueada para o usuário** nas configurações de segurança do ERP.

## 2. Contexto

No ERP Viasuper, os usuários operacionais não precisam memorizar regras complexas de movimentação de estoque, geração de contas a pagar/receber ou CFOPs. Toda essa inteligência comercial e fiscal fica embutida dentro da "Configuração de Documento". 

Dado o alto impacto que uma configuração pode ter (ex: uma configuração de "Ajuste de Estoque" pode baixar mercadorias do estoque sem gerar receita), o sistema bloqueia o acesso por padrão. O administrador precisa acessar as opções de segurança e habilitar ("desbloquear") quais configurações cada usuário pode utilizar em cada rotina. Sem essa liberação, a configuração fica invisível.

## 3. Condição (Se / Então)

### 3.1 — Direcionamento de Saldos e Operação
- **Se:** o usuário salva um documento (nota fiscal ou pedido) atrelado a uma Configuração de Documento;
- **Então:** o sistema lê as parametrizações vinculadas a essa configuração para determinar o comportamento do documento:
  1. **Natureza:** Define se é Compra, Venda, Transferência, Ajuste, etc.
  2. **Impacto no Estoque:** Define se movimenta estoque (entrada ou saída) e para qual local padrão.
  3. **Impacto Financeiro:** Define se gera duplicatas (Contas a Pagar/Receber) e se exige integração de recebimento/pagamento.

### 3.2 — Permissão e Visibilidade (Desbloqueio de Usuário)
- **Se:** o usuário abre a listagem (lookup) do campo de "Configuração de Documento" em uma tela de notas ou pedidos;
- **Então:** o sistema verifica a tabela de permissões no caminho *Configurações > Configurações de Usuário > Processos*.
  - Apenas as configurações marcadas como "desbloqueadas" para o grupo/usuário ativo na rotina atual serão exibidas.
  - Se o usuário digitar diretamente o código de uma configuração à qual não tem acesso, o sistema bloqueia a ação informando que
  não existe tal configuração.

### 3.3 — Herança para Pedidos
- **Se:** o administrador criar uma "Configuração de Pedido";
- **Então:** esta configuração será obrigatoriamente baseada e espelhará os comportamentos de estoque e financeiro da "Configuração de Documento" vinculada a ela.

## 4. Exemplos

### Válido — Usuário de Caixa com permissões restritas

Um operador de frente de loja abre a tela de notas. Ao consultar as Configurações de Documento, ele visualiza apenas "201 - Venda de mercadoria", pois apenas esta foi liberada para ele em *Configurações > Configurações de Usuário*. Ele não vê "Compra" nem "Ajuste de Estoque".

### Válido — Operação que não movimenta financeiro

O usuário seleciona a configuração "Ajuste de Estoque (Perdas)". Por parametrização interna desta configuração, o sistema realiza uma saída no estoque do produto, mas não exige e nem gera blocos financeiros de duplicatas.

### Inválido — Tentativa de uso sem permissão

O usuário tenta usar o código `5` (Nota de Crédito) digitando no campo. O sistema identifica que a configuração existe, porém não é exibida na tela, pois o usuario não tem permissão*

## 5. Exceções

- Caso a operação desejada (ex: um novo tipo de ajuste de estoque ou bonificação específica) ainda não possua uma configuração criada no sistema, o administrador deve primeiramente acessar **Cadastros > Configurações > Documento** para cadastrar a nova configuração, definindo seus impactos em saldos, antes de poder liberá-la para os usuários.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Liberação de Processos | Configurações > Configurações de Usuário > Processos | Define quais Configurações de Documento cada usuário/grupo pode enxergar e utilizar. |
| Configuração de Pedido | Configurações > Documentos > Configurações de Pedido | Rotina que herda o comportamento e a inteligência da Configuração de Documento. |
| Cadastro da Configuração | Cadastros > Configurações > Documento | Define se a configuração atualiza saldo, financeiro e qual a natureza da operação. |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-22 | 1.2 | Reescrita total da regra. Substituição do foco em "finalidade fiscal" por "impacto em saldos" e "permissões de usuário", refletindo a real arquitetura do Viasuper para controle de operações comerciais. |
| 2026-06-22 | 1.1 | Generalização inicial para abranger múltiplas rotinas (abandonada por focar incorretamente apenas na finalidade). |
| 2026-05-21 | 1.0 | Criação a partir da [AG-32021](https://nimitz.atlassian.net/browse/AG-32021). |
