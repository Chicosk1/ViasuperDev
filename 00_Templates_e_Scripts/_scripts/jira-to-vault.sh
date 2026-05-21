#!/bin/bash
# Wrapper para contornar o bug do Git Bash com argumentos no -m
# Uso: bash jira-to-vault.sh AG-31945 --tipo processo --dry-run
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$DIR/.venv/Scripts/python" -c "
import sys
sys.argv = sys.argv[1:]
from viasuperdev.cli import main
main()
" -- "$@"