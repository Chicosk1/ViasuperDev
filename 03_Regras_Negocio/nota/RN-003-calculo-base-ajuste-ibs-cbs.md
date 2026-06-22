---
id: RN-003
titulo: "Cálculo automático da base de ajuste tributário (IBS/CBS) em variações financeiras"
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
  - ibs
  - cbs
  - calculo
  - reforma-tributaria
  - ajuste
  - encargos
  - desconto
processos_relacionados:
  - PROC-001
  - PROC-002
  - PROC-003
padroes_relacionados: []
data_criacao: "2026-05-21"
data_revisao: "2026-06-19"
---

# Cálculo automático da base de ajuste tributário (IBS/CBS) em variações financeiras

## 1. Definição

Sempre que o ERP precisar calcular a **base tributável de ajuste** para IBS e CBS decorrente de variações financeiras em um documento fiscal ou registro financeiro (encargos como juros, multa e acréscimos, ou descontos concedidos/obtidos), o sistema deve calcular automaticamente esse valor aplicando a fórmula:

```
Base de Ajuste = Juros + Multa + Acréscimos − Desconto
```

O resultado positivo indica uma base de **débito fiscal** (encargos aumentaram o valor pago). O resultado negativo indica uma base de **crédito fiscal** (desconto reduziu o valor recebido). O usuário pode editar o valor calculado antes de confirmar.

Esta regra se aplica a qualquer rotina do ERP que precise apurar a base tributária de IBS/CBS sobre variações financeiras — incluindo geração de notas de crédito/débito, ajustes de baixa de duplicatas, notas de complemento e conciliações financeiras com impacto fiscal.

## 2. Contexto

Com a Reforma Tributária brasileira (IBS e CBS), os tributos incidem sobre o **valor efetivamente recebido ou pago** na operação. Quando uma transação resulta em valor diferente do original (devido a encargos ou descontos), a base de cálculo dos tributos precisa ser ajustada para refletir essa diferença. A fórmula unifica todas as variações positivas (acréscimos) e subtrai as negativas (descontos) para apurar o delta tributável de forma padronizada, garantindo conformidade com a legislação e consistência entre todas as rotinas do ERP.

## 3. Condição (Se / Então)

- **Se:** o sistema identificar um registro financeiro com variação financeira elegível (conforme [[RN-002-duplicatas-elegiveis]]) ou qualquer documento que exija cálculo de base de ajuste IBS/CBS;
- **Então:**
  1. O sistema calcula automaticamente:
     ```
     Base IBS à Ajustar = Juros + Multa + Acréscimos − Desconto
     Base CBS à Ajustar = Juros + Multa + Acréscimos − Desconto
     ```
  2. Preenche os campos correspondentes na tela com o valor calculado.
  3. Permite que o usuário edite manualmente o valor antes de confirmar (para casos onde o ajuste desejado difere do cálculo automático).
  4. **Resultado positivo (encargos > desconto):** base para geração de nota de débito / ajuste a recolher.
  5. **Resultado negativo (desconto > encargos):** base para geração de nota de crédito / ajuste a recuperar.

- **Se:** todos os campos de variação forem zero (registro não elegível per [[RN-002-duplicatas-elegiveis]]);
- **Então:** os campos de base de ajuste ficam com valor zero e o registro não deve ser processado.

## 4. Exemplos

### Válido — Encargos com resultado positivo (nota de débito)

Baixa de duplicata com atraso:
- Juros: R$ 50,00 | Multa: R$ 10,00 | Acréscimos: R$ 0,00 | Desconto: R$ 5,00

```
Base IBS à Ajustar = 50 + 10 + 0 − 5 = R$ 55,00  (positivo → nota de débito)
Base CBS à Ajustar = 50 + 10 + 0 − 5 = R$ 55,00
```

### Válido — Desconto com resultado negativo (nota de crédito)

Desconto por pagamento antecipado:
- Juros: R$ 0,00 | Multa: R$ 0,00 | Acréscimos: R$ 0,00 | Desconto: R$ 20,00

```
Base IBS à Ajustar = 0 + 0 + 0 − 20 = −R$ 20,00  (negativo → nota de crédito)
Base CBS à Ajustar = −R$ 20,00
```

### Válido — Encargos e desconto simultâneos

Negociação com acréscimo de armazenagem e desconto parcial:
- Acréscimos: R$ 30,00 | Desconto: R$ 10,00

```
Base IBS à Ajustar = 0 + 0 + 30 − 10 = R$ 20,00  (nota de débito sobre o líquido)
```

### Inválido

O sistema deixar os campos de base de ajuste em branco e exigir que o operador calcule e preencha manualmente. A automação é obrigatória para garantir padronização e conformidade.

## 5. Exceções

- O usuário pode **editar manualmente** os valores calculados antes de confirmar o processamento, para casos onde há negociação específica ou correção de arredondamento.
- Quando o resultado for exatamente zero (encargos = descontos), o registro tecnicamente cumpre os critérios da [[RN-002-duplicatas-elegiveis]] (há valores maiores que zero), mas a base de ajuste líquida é zero — nesse caso, o sistema deve alertar o usuário antes de gerar o documento fiscal, pois uma nota com base zero pode ser rejeitada pela SEFAZ.

## 6. Parâmetros do ERP Envolvidos

Nenhum parâmetro de configuração — cálculo fixo e automático baseado nos valores financeiros do registro. A fórmula é imutável por definição da legislação tributária.

## 7. Histórico

| Data | Versão | Mudança |
|---|---|---|
| 2026-06-19 | 1.1 | Generalização da regra para abranger qualquer rotina do ERP que calcule base de ajuste IBS/CBS sobre variações financeiras. Adição do cenário de encargos e desconto simultâneos, e do alerta para base líquida zero. |
| 2026-05-21 | 1.0 | Criação a partir da [AG-31945](https://nimitz.atlassian.net/browse/AG-31945) (critérios 3.7 e 3.8) |
