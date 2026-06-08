# ─────────────────────────────────────────────────────────────
# Makefile — ViasuperDev Scripts
# Executar dentro de: 00_Templates_e_Scripts/_scripts/
# Uso: make <comando>
# ─────────────────────────────────────────────────────────────

PYTHON  = .venv/Scripts/python
PIP     = .venv/Scripts/python -m pip
RUFF    = .venv/Scripts/python -m ruff
PYTEST  = .venv/Scripts/python -m pytest
MYPY    = .venv/Scripts/python -m mypy

.PHONY: setup install test test-cov lint typecheck format check clean help

## Cria o ambiente virtual e instala todas as dependências
setup:
	python -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	@echo ""
	@echo "Ambiente pronto. Copie .env.example para .env e preencha as credenciais."

## Instala apenas dependências de produção
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

## Executa todos os testes com output detalhado
test:
	$(PYTEST) tests/ -v

## Executa testes com relatório de cobertura
test-cov:
	$(PYTEST) tests/ -v --cov=viasuperdev --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Relatório HTML gerado em: htmlcov/index.html"

## Verifica estilo e erros de lint
lint:
	$(RUFF) check viasuperdev/ tests/

## Verifica tipos estáticos
typecheck:
	$(MYPY) viasuperdev/

## Corrige formatação e imports automaticamente
format:
	$(RUFF) check --fix viasuperdev/ tests/
	$(RUFF) format viasuperdev/ tests/

## Roda lint + typecheck + testes
check: lint typecheck test

## Remove arquivos gerados
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "Cache limpo."

## Remove tudo incluindo o .venv
clean-all: clean
	rm -rf .venv/
	@echo ".venv removido. Execute 'make setup' para recriar."

## Exibe este menu de ajuda
help:
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^##' Makefile | sed 's/## /  /'
	@echo ""

.PHONY: index index-full index-stats query

index:
	python -m viasuperdev.indexer --only kb

index-full:
	python -m viasuperdev.indexer --only kb --full

index-dry:
	python -m viasuperdev.indexer --only kb --dry-run

index-stats:
	python -m viasuperdev.indexer --stats

# Uso: make query Q="base IBS ajustar"
query:
	@python -m viasuperdev.indexer --query "$(Q)"