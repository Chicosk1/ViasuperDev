---
tipo: processo_erp
modulo: Nota
versao_erp: 5.0.2503.1004
status: em andamento
---

# Gerar Notas de Crédito/Débito

## 1. Escopo e Objetivo do Processo
*Viasuper » Processos » Nota » Gerar Notas de Crédito/Débito*

Esta rotina foi desenvolvida para simplificar e automatizar o gerenciamento de notas fiscais de ajuste. Ela permite que um analista financeiro gere, em massa, Notas de Crédito e Notas de Débito a partir de juros, multas, adiantamentos, acréscimos e descontos registrados nas baixas de duplicatas (a receber ou a pagar).

O processo resolve o problema do cálculo e digitação manuais desses documentos, garantindo o ajuste correto, proporcional e alinhado aos valores de IBS e CBS das notas fiscais de origem, atendendo especialmente empresas com grande volume diário de movimentações financeiras.

## 2. Regras de Negócio e Restrições (Lógica)
* **Validação de Filtros Mínimos:** O processo de busca não pode ser executado se ambos os campos de intervalo de datas (Emissão e Data de Baixa) estiverem nulos. Ao menos um período deve ser informado.

* **Obrigatoriedade de Configuração de Documento:** Para executar a geração das notas, é obrigatório informar uma Configuração de Documento válida.

* **Restrição de Finalidade do Documento:** O campo de configuração de documentos só deve exibir e aceitar parametrizações cuja finalidade de emissão seja igual a 5 (Nota de Crédito) ou 6 (Nota de Débito).

* **Filtro de Relevância Financeira:** A consulta inicial só deve retornar duplicatas que possuam valores maiores que zero em pelo menos um dos campos: multa, juros, descontos ou acréscimos.

* **Cálculo da Base de Ajuste Sugerida:** Ao listar os registros, o sistema deve calcular e preencher automaticamente os campos editáveis Base IBS à Ajustar e Base CBS à Ajustar utilizando a seguinte lógica: `Base a Ajustar=Juros+Multa+Acrescimos-Desconto`

* **Regra de Clivagem por Valor Mínimo (Rateio):** Itens cujo valor de imposto calculado (IBS/CBS) após o rateio proporcional resulte em um valor inferior a R$ 0,01 não deverão ser referenciados na nota fiscal gerada.

* **Premissas para Emissão de NF-e:** Para que o documento gerado seja transmitido com sucesso à Sefaz, o sistema exige certificado digital configurado (Configurações > Gerais > Filial > Configuração NFE), ambiente parametrizado (Homologação ou Produção) e o DFe devidamente ativo.

## 3. Fluxo do Processo (Passo a Passo)
1. **Filtro e Seleção**

    1. O usuário acessa o menu Processos » Nota » Gerar Notas de Crédito/Débito.
    2. Define os parâmetros de busca (Estabelecimento, Pessoa, Portador, Datas, Tipo de Duplicata).
    3. O usuário clica em Executar. O sistema valida o preenchimento das datas e busca os registros no banco de dados.
    4. O grid exibe as duplicatas e as respectivas baixas (se houver mais de uma baixa parcial para a mesma duplicata, ela será listada em linhas separadas).
    5. O usuário seleciona quais registros deseja processar marcando a flag Gerar e clica no botão Próximo.

2. **Parametrização e Distribuição**

    1. O ERP carrega a segunda tela contendo apenas os registros selecionados no passo anterior.
    2. O usuário confere/ajusta os valores das colunas Base IBS à Ajustar e Base CBS à Ajustar se necessário.
    3. O usuário seleciona a Configuração de Documento (Validando restrição de finalidade 5 ou 6).
    4. O usuário clica em Gerar Notas.

3. **Processamento e Gravação**
    
    1. O sistema inicia um laço de repetição pelos registros selecionados e exibe uma barra de progresso na tela.
    2. Para cada registro, o ERP recupera os itens da nota fiscal de origem e realiza o rateio proporcional dos valores informados de ajuste, baseando-se na representação financeira de cada item sobre o valor total da nota de origem.
    3. O sistema calcula o IBS e CBS por item a partir da nova base distribuída, descartando as linhas com imposto menor que R$ 0,01.
    4. São gravadas as novas notas fiscais (com seus respectivos itens, valores unitários/totais ajustados, impostos e referências de origem) no estabelecimento de origem da duplicata.
    5. A barra de progresso é finalizada e o feedback de conclusão é exibido ao usuário.

## 4. Arquitetura Técnica e Código (Delphi / Oracle)
* **Componente de Interface:** Nova rotina integrada ao menu padrão do ERP Viasuper.
* **Tabelas do Banco:** `DUPREC`, `DUPPAG`, `DUPRECACERFIN`, `DUPPAGACERFIN`, `ACERDRE`, `ACERDPA`, `ACERFIN`, `NOTA`, `NOTAITEM`, `NOTAACERFIN`, `PESSOADOC`, `NOTAITEMIMPOSTOIVA`.

**Trecho de Código Crítico:**
``` pascal
procedure TFGeraNotaCredDeb.CarregarNotaCredDeb;
begin
  cdsGeraNotaCredDeb.Close;
  cdsGeraNotaCredDeb.ClearFilter;

  cdsGeraNotaCredDeb.Data := DmConexao.QueryPegaData(FConsulta       ,                         '*',
                                                    ['?',       '1:s',                  GetFiltros,
                                                     'P',  'DTINIEMI', DataNull(drEmissaoINI.Data),
                                                     'P',  'DTFIMEMI', DataNull(drEmissaoFIM.Data),
                                                     'P',  'DTINIBX' , DataNull(drBaixaINI.Data)  ,
                                                     'P',  'DTFIMBX' , DataNull(drBaixaFIM.Data) ],
                                                    [ftString, ftDate, ftDate,   ftDate,   ftDate],
                                                    [1000,     0,      0,        0,             0]);
end;
```

## 5. Casos de Falha Comuns (Troubleshooting)
* **Nenhum registro retornado na busca:** 
    * Causa: As duplicatas no período filtrado não possuem valores de juros, multa, acréscimo ou desconto em suas baixas, ou nenhuma baixa foi realizada no intervalo informado.

    * Solução: Verificar no módulo financeiro se a duplicata em questão possui os lançamentos de taxas/descontos na tela de baixa.

* **Configuração de Documento não aparece na listagem:** 
    * Causa: O cadastro da configuração selecionada está com o campo "Finalidade de Emissão" diferente de 5 - Nota de Crédito ou 6 - Nota de Débito.

    * Solução: Acessar o cadastro de configurações de documentos do ERP e ajustar a finalidade para o tipo correto.

* **Item da nota fiscal original sumiu na nota de ajuste:** 
    *  Causa: O valor do rateio proporcional resultou em uma base de cálculo cujo imposto final devido ficou abaixo de R$ 0,01. Conforme a regra de negócio, o sistema intencionalmente omitiu o item para evitar rejeições na Sefaz.

    *  Solução: Comportamento esperado. Caso seja estritamente necessária a presença do item, verifique se o valor total do ajuste inserido no grid não está excessivamente baixo.

* **Erro de Rejeição da Sefaz ao transmitir a Nota Gerada:** 
    *  Causa: Certificado digital expirado, falta de amarração de documentos fiscais referenciados (chave de acesso da nota de origem ausente) ou ambiente inconsistente.

    *  Solução: Validar os parâmetros de DFe na filial e conferir se a nota que originou a duplicata está devidamente autorizada na Sefaz.