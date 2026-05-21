# ViasuperDev Scripts

Automação para o pipeline **Jira → Obsidian vault → Claude Code**.

## Pré-requisitos

- Python 3.11+
- Acesso à instância Jira Nimitz

## Setup

```bash
# 1. Clone ou copie esta pasta para o vault
cd 00_Templates_e_Scripts/_scripts

# 2. Crie o ambiente virtual e instale dependências
make setup

# 3. Configure as credenciais
cp .env.example .env
# Edite o .env com seu editor
```

## Uso

```bash
# Gera AG a partir de um ticket Jira
jira-to-vault AG-XXXXX

# Gera rascunho de processo
jira-to-vault AG-XXXXX --tipo processo

# Visualiza sem salvar
jira-to-vault AG-XXXXX --dry-run
```

## Desenvolvimento

```bash
# Roda todos os testes
make test

# Verifica lint e tipos antes de commitar
make check

# Formata o código
make format
```

## Estrutura

```
viasuperdev/
├── config.py        # Configuração centralizada
├── jira_client.py   # Cliente Jira
├── parsers.py       # Extração de dados ADF
├── vault_writer.py  # Escrita no vault
└── cli.py           # Entry point dos comandos
templates/
├── ag.j2            # Template AG
└── processo.j2      # Template Processo
tests/
├── test_parsers.py     
└── test_vault_writer.py
```