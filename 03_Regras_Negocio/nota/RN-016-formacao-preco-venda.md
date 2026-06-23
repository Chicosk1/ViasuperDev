---
id: RN-016
titulo: "Repasse de Custo de Entrada para Formação de Preço de Venda"
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
  - precificacao
  - custo
  - nota-fiscal
  - importacao-xml
  - preco-venda
processos_relacionados:
  - PROC-002
  - PROC-003
padroes_relacionados: []
data_criacao: "2026-06-19"
data_revisao: "2026-06-19"
---

# Repasse de Custo de Entrada para Formação de Preço de Venda

## 1. Definição

Ao concluir a entrada de uma nota fiscal de compra (importada via XML ou lançada manualmente), o sistema pode automaticamente **atualizar o custo de entrada** dos produtos no cadastro do ERP e **direcionar o usuário para a rotina de precificação**, permitindo a revisão e o ajuste do preço de venda com base no novo custo apurado. Este repasse garante que as margens de lucro da loja sejam mantidas frente a variações de custo do fornecedor.

Esta regra se aplica a notas fiscais de entrada, importação de XML (NF-e) e qualquer rotina do ERP que registre entradas de mercadoria com valor de custo atualizado.

## 2. Contexto

O preço de custo de um produto é um dado dinâmico que varia a cada entrega do fornecedor (inflação, negociação de frete, mudanças de tributação, etc.). Se o preço de venda da loja não for revisado após uma mudança de custo, a margem de lucro pode ser comprimida ou até negativa. O ERP facilita esse processo ao calcular automaticamente o novo custo de entrada (custo médio ou custo de última entrada, conforme configuração) e oferecer acesso direto à tela de formação de preço de venda logo após o fechamento da nota.

## 3. Condição (Se / Então)

- **Se:** o usuário salva/finaliza uma nota fiscal de entrada com sucesso;
- **Então:**
  1. O sistema calcula o **novo custo de entrada** de cada produto da nota, considerando:
     - Valor do item (preço unitário × quantidade).
     - Rateio proporcional de frete, seguro e despesas acessórias ([[RN-004-rateio-proporcional-itens]]).
     - Impostos recuperáveis (ICMS, PIS, COFINS — conforme regime tributário do destinatário).
  2. Atualiza o campo de **Custo de Entrada** no cadastro do produto com o valor calculado.
  3. (Conforme parametrização) Recalcula o **Custo Médio** do produto com base no saldo anterior e na nova entrada.
  4. Exibe ao usuário uma notificação ou redireciona para a **rotina de Precificação/Formação de Preço de Venda**, listando os produtos da nota que tiveram variação de custo.
  5. O usuário pode aceitar a sugestão de novo preço (gerada pelo sistema com base no markup configurado) ou ajustar manualmente antes de confirmar.

## 4. Exemplos

### Válido — Entrada de arroz com aumento de custo

Produto: Arroz Tipo 1 5kg
- Custo anterior: R$ 12,50/un
- Nova NF: R$ 13,80/un (aumento de 10,4%)
- Sistema atualiza custo de entrada para R$ 13,80 e calcula novo preço de venda sugerido com markup 30%: R$ 17,94.
- Usuário revisa e confirma o novo preço na tela de precificação.

### Válido — Produto com custo médio ponderado

Saldo anterior: 50 un × R$ 12,50 = R$ 625,00
Nova entrada: 100 un × R$ 13,80 = R$ 1.380,00
Custo médio = (625 + 1.380) / 150 = **R$ 13,37/un**

### Inválido

O sistema não deve atualizar o preço de venda automaticamente sem a confirmação do usuário. A atualização do preço de venda é sempre uma ação deliberada do operador, nunca automática e silenciosa.

## 5. Exceções

- Produtos do tipo **Serviço** ou **Composição** não têm custo de entrada atualizado pela nota fiscal de compra.
- Notas de **Bonificação** (mercadoria sem custo financeiro) atualizam o estoque mas não alteram o custo de entrada do produto.
- Se o ERP estiver configurado para usar **Custo de Última Entrada** (em vez de Custo Médio), cada nova nota sobrescreve o custo independentemente do saldo anterior.

## 6. Parâmetros do ERP Envolvidos

| Parâmetro | Localização | Efeito |
|---|---|---|
| Método de custeio | Configurações > Estoque | Define se usa Custo Médio Ponderado ou Custo de Última Entrada |
| Markup por produto/grupo | Cadastro do Produto / Grupo Mercadológico | Base para o cálculo do preço de venda sugerido |
| Impostos recuperáveis | Configurações > Fiscal > Tributação | Define quais impostos entram no custo líquido do produto |
| Redirecionamento para Precificação | Configurações > Gerais > Entrada de NF | Define se o sistema redireciona automaticamente após salvar a nota |

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.0 | Criação da regra com base nos PDFs de Importação NF-e e Nota Fiscal |
