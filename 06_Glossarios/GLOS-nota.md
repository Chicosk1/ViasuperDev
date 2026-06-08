---
id: GLOS-nota
titulo: "Glossário — Nota Fiscal e Reforma Tributária"
tipo: glossario
modulo: "nota"
status: ativo
versao_template: "1.0"
contexto_llm: alto
tags:
  - glossario
  - nota
  - nfe
  - ibs
  - cbs
  - reforma-tributaria
  - fiscal
total_termos: 26
data_criacao: "2026-05-21"
data_revisao: "2026-05-21"
---

# Glossário — Nota Fiscal e Reforma Tributária

<!--
  Uma entrada por termo. Cada ### vira um chunk independente no RAG.
  Nunca agrupe dois termos sob o mesmo ###.
  Atualize total_termos no frontmatter ao adicionar ou remover entradas.
-->

---

### IBS

- **Definição:** Imposto sobre Bens e Serviços — tributo criado pela Reforma Tributária (EC 132/2023) que substitui o ICMS (estadual) e o ISS (municipal), com alíquota única por operação dividida entre estado e município.
- **Contexto de uso:** Aparece nos impostos das notas fiscais como base e valor de IBS, dividido em IBS estadual (`IBSUF`) e IBS municipal (`IBSMUN`). Calculado sobre o valor efetivamente recebido/pago, incluindo ajustes de juros, multas e descontos.
- **Sinônimos / variações:** IBS, Imposto sobre Bens e Serviços
- **Não confundir com:** [[GLOS-nota#ICMS]] — IBS substitui o ICMS na reforma tributária
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### IBSUF

- **Definição:** Parcela do IBS destinada ao Estado (Unidade Federativa) — componente estadual do Imposto sobre Bens e Serviços.
- **Contexto de uso:** Armazenado separadamente de `IBSMUN` na tabela `NOTAITEMIMPOSTOIVA`. A alíquota é configurada no cadastro de tributação IVA.
- **Sinônimos / variações:** IBS Estadual, IBS UF
- **Não confundir com:** [[GLOS-nota#IBSMUN]] — parcela municipal do IBS
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### IBSMUN

- **Definição:** Parcela do IBS destinada ao Município — componente municipal do Imposto sobre Bens e Serviços.
- **Contexto de uso:** Armazenado separadamente de `IBSUF` na tabela `NOTAITEMIMPOSTOIVA`. Junto com `IBSUF` compõe o valor total de IBS da operação.
- **Sinônimos / variações:** IBS Municipal, IBS Mun
- **Não confundir com:** [[GLOS-nota#IBSUF]] — parcela estadual do IBS
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### CBS

- **Definição:** Contribuição sobre Bens e Serviços — tributo federal criado pela Reforma Tributária que substitui o PIS e a COFINS, com alíquota única federal.
- **Contexto de uso:** Aparece nos itens das notas fiscais como base e valor de CBS. Calculado sobre o mesmo valor base do IBS — ajustes de juros, multas e descontos impactam igualmente a base de CBS.
- **Sinônimos / variações:** CBS, Contribuição sobre Bens e Serviços
- **Não confundir com:** [[GLOS-nota#IBS]] — IBS é o imposto sub-nacional (estado + município); CBS é o tributo federal
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### Base

- **Definição:** Valor monetário sobre o qual a alíquota de um imposto é aplicada para obter o valor do tributo devido.
- **Contexto de uso:** No contexto de IBS e CBS, a base pode sofrer reduções. As colunas `Base Total IBS` e `Base Total CBS` na rotina de Notas de Crédito/Débito representam a base da nota de origem.
- **Sinônimos / variações:** Base de cálculo, Base tributável
- **Não confundir com:** [[GLOS-nota#Alíquota]]

---

### Alíquota

- **Definição:** Percentual aplicado sobre a base de cálculo para determinar o valor do imposto devido.
- **Contexto de uso:** Configurada por no cadastro de Tributações, possuindo variaveis de acordo com cada Imposto (IVA, ICMS, PIS, COFINS, etc...). Utilizada no rateio proporcional de IBS/CBS nos itens da nota de crédito/débito gerada — conforme [[RN-004-rateio-proporcional-itens]].
- **Sinônimos / variações:** Alíquota efetiva, taxa
- **Não confundir com:** [[GLOS-nota#Base]]

---

### Redução de Base de Cálculo

- **Definição:** Percentual pelo qual a base de um imposto é reduzida antes da aplicação da alíquota, diminuindo o valor efetivo do tributo sem alterar a alíquota nominal.
- **Contexto de uso:** Deve ser respeitada no cálculo dos valores de IBS e CBS após o rateio proporcional nos itens da nota de crédito/débito — conforme [[RN-004-rateio-proporcional-itens]].
- **Sinônimos / variações:** Redução de base, benefício fiscal

---

### CFOP

- **Definição:** Código Fiscal de Operações e Prestações — código de 4 dígitos que classifica a natureza de uma operação fiscal (venda, devolução, transferência, etc.) e determina o tratamento tributário aplicável.
- **Contexto de uso:** O primeiro dígito indica o tipo de operação (1/2 = entrada estadual/interestadual, 5/6 = saída estadual/interestadual, 7 = exportação).
- **Sinônimos / variações:** CFOP, Código Fiscal
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### NF-e

- **Definição:** Nota Fiscal Eletrônica — documento fiscal de existência exclusivamente digital, cuja validade jurídica é garantida pela assinatura digital do emitente e pela autorização da Sefaz.
- **Contexto de uso:** Formato de emissão das notas de crédito e débito geradas pela rotina [[PROC-001-gerar-notas-credito-debito-massa]]. Requer certificado digital e comunicação com a Sefaz para autorização.
- **Sinônimos / variações:** NF-e, Nota Eletrônica
- **Não confundir com:** [[GLOS-nota#DANFE]] — o DANFE é apenas a representação impressa da NF-e
- **Processos relacionados:** [[PROC-001-gerar-notas-credito-debito-massa]]

---

### DANFE

- **Definição:** Documento Auxiliar da Nota Fiscal Eletrônica — representação gráfica simplificada da NF-e em papel, sem valor fiscal próprio, usado para acompanhar a mercadoria em trânsito.
- **Contexto de uso:** Gerado no Viasuper após a autorização da NF-e pela Sefaz. Não substitui a NF-e; é apenas sua representação impressa.
- **Sinônimos / variações:** DANFE, Documento Auxiliar
- **Não confundir com:** [[GLOS-nota#NF-e]] — a NF-e é o documento fiscal; o DANFE é só a impressão

---

### DFe

- **Definição:** Documentos Fiscais Eletrônicos — infraestrutura e configuração no Viasuper responsável pela comunicação com a Sefaz para transmissão, recepção e consulta de documentos fiscais eletrônicos (NF-e, CT-e, MDF-e, etc.).
- **Contexto de uso:** Deve estar devidamente configurado como pré-condição para a emissão de documentos fiscais.
- **Sinônimos / variações:** DFe, DF-e

---

### Sefaz

- **Definição:** Secretaria da Fazenda Estadual — órgão responsável pela autorização e registro das Notas Fiscais Eletrônicas. A comunicação é feita via webservice com o certificado digital do emitente.
- **Contexto de uso:** As notas de crédito/débito geradas pela rotina ficam disponíveis para transmissão manual à Sefaz após a geração.
- **Sinônimos / variações:** Sefaz, SEFAZ, Secretaria da Fazenda

---

### Nota de Crédito

- **Definição:** Nota fiscal emitida para ajustar para menor o valor de IBS e CBS de uma operação anterior, decorrente de desconto concedido na baixa de duplicata.
- **Contexto de uso:** Gerada pela rotina [[PROC-001-gerar-notas-credito-debito-massa]] quando o valor de `Base IBS/CBS à Ajustar` é negativo (desconto > encargos). Requer configuração de documento com finalidade `5 - Nota de Crédito` — conforme [[RN-006-configuracao-documento-finalidade]].
- **Sinônimos / variações:** Nota de crédito, NC
- **Não confundir com:** [[GLOS-nota#Nota de Débito]]

---

### Nota de Débito

- **Definição:** Nota fiscal emitida para ajustar para maior o valor de IBS e CBS de uma operação anterior, decorrente de juros, multas ou acréscimos cobrados na baixa de duplicata.
- **Contexto de uso:** Gerada pela rotina [[PROC-001-gerar-notas-credito-debito-massa]] quando o valor de `Base IBS/CBS à Ajustar` é positivo (encargos > desconto). Requer configuração de documento com finalidade `6 - Nota de Débito` — conforme [[RN-006-configuracao-documento-finalidade]].
- **Sinônimos / variações:** Nota de débito, ND
- **Não confundir com:** [[GLOS-nota#Nota de Crédito]]

---

### Configuração de Documento

- **Definição:** Cadastro no Viasuper que define os parâmetros fiscais de emissão de um tipo de documento (série, modelo, CFOP padrão, finalidade de emissão, etc.).
- **Contexto de uso:** Armazenado na tabela `NOTACONF`, possui regras para emissão de documentos fiscais.
- **Sinônimos / variações:** Conf. de documento, Config. documento

---

### Duplicata

- **Definição:** Título de crédito que representa uma obrigação de pagamento decorrente de uma compra e venda mercantil ou prestação de serviços. No Viasuper, pode ser a receber (`DUPREC`) ou a pagar (`DUPPAG`).
- **Contexto de uso:** Uma duplicata pode ter múltiplas baixas parciais.
- **Sinônimos / variações:** Duplicata, título, boleto
- **Não confundir com:** [[GLOS-nota#Fatura]] — a fatura agrupa duplicatas; a duplicata é o título individual

---

### Fatura

- **Definição:** Documento que agrupa uma ou mais duplicatas referentes a uma mesma operação comercial. Identificada pelo campo `FATURA` nas tabelas `DUPREC` e `DUPPAG`.
- **Contexto de uso:** Permite restringir a busca a duplicatas de uma fatura específica.
- **Sinônimos / variações:** Fatura, número de fatura
- **Não confundir com:** [[GLOS-nota#Duplicata]]

---

### Baixa

- **Definição:** Registro do recebimento ou pagamento total ou parcial de uma duplicata, podendo incluir valores de juros, multa, acréscimos e descontos em relação ao valor original.
- **Contexto de uso:** Uma duplicata pode ter múltiplas baixas parciais.
- **Sinônimos / variações:** Baixa financeira, liquidação, quitação parcial

---

### Juros

- **Definição:** Encargo financeiro cobrado pelo atraso no pagamento de uma duplicata, calculado sobre o valor em aberto pelo período de atraso.
- **Sinônimos / variações:** Juros de mora, encargos de juros

---

### Multa

- **Definição:** Penalidade financeira de valor fixo ou percentual cobrada pelo atraso no pagamento de uma duplicata, distinta dos juros.
- **Sinônimos / variações:** Multa por atraso, multa moratória

---

### Acréscimo

- **Definição:** Valor adicional cobrado na baixa de uma duplicata que não se enquadra como juros ou multa (ex: taxas bancárias, despesas de cobrança).
- **Sinônimos / variações:** Acréscimos, encargos adicionais

---

### Desconto

- **Definição:** Redução concedida sobre o valor da duplicata no momento da baixa, por pagamento antecipado ou negociação comercial.
- **Sinônimos / variações:** Desconto financeiro, abatimento

---

### Rateio

- **Definição:** Distribuição de um valor total entre múltiplos itens de forma proporcional à participação de cada item no valor total do conjunto.
- **Sinônimos / variações:** Rateio Proporcional, distribuição proporcional

---

### Portador

- **Definição:** Entidade (banco, caixa ou carteira) responsável pela custódia e cobrança de duplicatas. Identificado pelo campo `IDPORTADOR` na tabela `PORTADOR`.
- **Sinônimos / variações:** Portador, banco cobrador, carteira de cobrança

---

### ICMS

- **Definição:** Imposto sobre Circulação de Mercadorias e Serviços — tributo estadual vigente antes da Reforma Tributária (EC 132/2023), substituído pelo IBS no novo regime tributário. Ainda vigente durante o período de transição.
- **Contexto de uso:** Referenciado em notas fiscais emitidas no regime anterior à reforma. Durante a transição, pode coexistir com o IBS em operações mistas.
- **Sinônimos / variações:** ICMS, Imposto sobre Circulação de Mercadorias
- **Não confundir com:** [[GLOS-nota#IBS]] — o IBS substitui o ICMS na reforma tributária

---

### ISS

- **Definição:** Imposto Sobre Serviços de qualquer natureza — tributo municipal vigente antes da Reforma Tributária (EC 132/2023), substituído pelo IBS no novo regime tributário.
- **Contexto de uso:** Referenciado em documentos fiscais de prestação de serviços emitidos no regime anterior. Junto com o ICMS, compõe os impostos sub-nacionais substituídos pelo IBS.
- **Sinônimos / variações:** ISS, ISSQN
- **Não confundir com:** [[GLOS-nota#IBS]] — o IBS substitui o ISS (municipal) e o ICMS (estadual)