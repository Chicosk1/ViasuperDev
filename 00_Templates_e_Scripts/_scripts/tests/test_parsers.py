"""
test_parsers.py — Testes unitários para parsers.py.

Roda com: make test
"""

from __future__ import annotations

import pytest

from viasuperdev.jira_client import JiraIssue
from viasuperdev.parsers import (
    adf_to_text,
    clean,
    extract_criterios,
    extract_fluxo,
    parse_ag,
    parse_processo,
    resolve_modulo,
    resolve_prioridade,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_issue(**overrides) -> JiraIssue:
    """Factory de JiraIssue para testes — valores padrão seguros."""
    defaults = dict(
        key="AG-99999",
        summary="Ticket de teste",
        description={},
        status="Backlog",
        issue_type="Melhoria",
        priority="Medium",
        assignee="Dev Teste",
        reporter="PO Teste",
        created="2026-01-01",
        updated="2026-01-01",
        components=[],
        labels=[],
        versao_sistema="",
        url="https://nimitz.atlassian.net/browse/AG-99999",
    )
    defaults.update(overrides)
    return JiraIssue(**defaults)


ADF_SIMPLE = {
    "type": "doc",
    "content": [
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": "Primeiro parágrafo."}],
        },
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": "Segundo parágrafo."}],
        },
    ],
}

ADF_WITH_LIST = {
    "type": "doc",
    "content": [
        {
            "type": "orderedList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Passo um"}],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Passo dois"}],
                        }
                    ],
                },
            ],
        }
    ],
}

ADF_WITH_HEADING = {
    "type": "doc",
    "content": [
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Título da seção"}],
        },
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": "Conteúdo da seção."}],
        },
    ],
}


# ── Testes: adf_to_text ───────────────────────────────────────────────────────

class TestAdfToText:
    def test_none_retorna_string_vazia(self):
        assert adf_to_text(None) == ""

    def test_dict_vazio_retorna_string_vazia(self):
        assert adf_to_text({}) == ""

    def test_paragrafo_simples(self):
        result = adf_to_text(ADF_SIMPLE)
        assert "Primeiro parágrafo." in result
        assert "Segundo parágrafo." in result

    def test_lista_ordenada(self):
        result = adf_to_text(ADF_WITH_LIST)
        assert "1. Passo um" in result
        assert "2. Passo dois" in result

    def test_heading(self):
        result = adf_to_text(ADF_WITH_HEADING)
        assert "## Título da seção" in result
        assert "Conteúdo da seção." in result

    def test_texto_com_marcacao_strong(self):
        node = {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "negrito",
                    "marks": [{"type": "strong"}],
                }
            ],
        }
        assert "**negrito**" in adf_to_text(node)

    def test_texto_com_code(self):
        node = {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "PERMITE_ESTOQUE_NEGATIVO",
                    "marks": [{"type": "code"}],
                }
            ],
        }
        assert "`PERMITE_ESTOQUE_NEGATIVO`" in adf_to_text(node)

    def test_hard_break(self):
        node = {"type": "hardBreak"}
        assert adf_to_text(node) == "\n"


# ── Testes: extract_criterios ─────────────────────────────────────────────────

class TestExtractCriterios:
    def test_padrao_nimitz_numerado(self):
        text = "3.1 - Critério: Botão Próximo deve aparecer\n3.2 - Critério: Tela deve carregar"
        result = extract_criterios(text)
        assert len(result) == 2
        assert "3.1" in result[0]
        assert "3.2" in result[1]

    def test_fallback_entao(self):
        text = "Quando clicar no botão\nEntão o sistema deve exibir a confirmação ao usuário"
        result = extract_criterios(text)
        assert len(result) >= 1
        assert "confirmação" in result[0].lower()

    def test_sem_criterios_retorna_placeholder(self):
        result = extract_criterios("Texto sem critérios definidos aqui.")
        assert len(result) == 1
        assert "manualmente" in result[0].lower()


# ── Testes: extract_fluxo ─────────────────────────────────────────────────────

class TestExtractFluxo:
    def test_extrai_passos_numerados(self):
        text = "1. Acessar a rotina de importação\n2. Selecionar o arquivo\n3. Confirmar operação"
        result = extract_fluxo(text)
        assert len(result) == 3
        assert "Acessar" in result[0]

    def test_sem_fluxo_retorna_placeholder(self):
        result = extract_fluxo("Texto sem passos numerados.")
        assert "análise" in result[0].lower()


# ── Testes: resolve_modulo ────────────────────────────────────────────────────

class TestResolveModulo:
    def test_usa_componente_do_jira(self):
        issue = make_issue(components=["Nota Fiscal"])
        assert resolve_modulo(issue) == "Nota Fiscal"

    def test_extrai_do_padrao_breadcrumb(self):
        # Com 3 segmentos: "» Financeiro » Baixa" → penúltimo = "Financeiro"
        issue = make_issue(
            components=[],
            description={
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Viasuper » Financeiro » Baixa",
                            }
                        ],
                    }
                ],
            },
        )
        assert resolve_modulo(issue) == "Financeiro"

    def test_extrai_penultimo_segmento_breadcrumb_longo(self):
        # Com 4 segmentos: "» Processos » Nota » Nota Fiscal" → penúltimo = "Nota"
        issue = make_issue(
            components=[],
            description={
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Viasuper » Processos » Nota » Nota Fiscal",
                            }
                        ],
                    }
                ],
            },
        )
        assert resolve_modulo(issue) == "Nota"

    def test_fallback_geral(self):
        issue = make_issue(components=[], description={})
        assert resolve_modulo(issue) == "Geral"


# ── Testes: resolve_prioridade ────────────────────────────────────────────────

class TestResolvePrioridade:
    @pytest.mark.parametrize("jira,esperado", [
        ("Highest", "alta"),
        ("High",    "alta"),
        ("Medium",  "media"),
        ("Low",     "baixa"),
        ("Lowest",  "baixa"),
        ("",        "media"),
    ])
    def test_mapeamento(self, jira: str, esperado: str):
        assert resolve_prioridade(jira) == esperado


# ── Testes: parse_ag ──────────────────────────────────────────────────────────

class TestParseAG:
    def test_retorna_parsed_ag(self):
        issue  = make_issue(description=ADF_SIMPLE)
        result = parse_ag(issue)
        assert result.modulo == "Geral"
        assert result.prioridade == "media"
        assert isinstance(result.criterios, list)
        assert len(result.criterios) >= 1

    def test_campos_nunca_sao_none(self):
        issue  = make_issue(description={})
        result = parse_ag(issue)
        assert result.contexto
        assert result.objetivo
        assert result.escopo_inclui
        assert result.escopo_nao_inclui
        assert result.referencias
        assert result.resultado_esperado


# ── Testes: parse_processo ────────────────────────────────────────────────────

class TestParseProcesso:
    def test_retorna_parsed_processo(self):
        issue  = make_issue(description=ADF_WITH_LIST)
        result = parse_processo(issue)
        assert isinstance(result.fluxo, list)
        assert len(result.fluxo) >= 1

    def test_objetivo_nunca_vazio(self):
        issue  = make_issue(description={})
        result = parse_processo(issue)
        assert result.objetivo