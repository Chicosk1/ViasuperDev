"""
cli.py — Interface de linha de comando.

Responsabilidade única: parsear argumentos e orquestrar
os outros módulos. Nenhuma lógica de negócio aqui.
"""

from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from viasuperdev import config
from viasuperdev.logging_config import setup_logging
from viasuperdev.jira_client import JiraClient, JiraClientError
from viasuperdev.parsers import (
    extract_nome_rotina,
    parse_ag,
    parse_processo,
    prompt_nome_rotina,
)
from viasuperdev.vault_writer import find_processo, merge_processo, write_ag, write_processo

log = logging.getLogger(__name__)

TIPOS_DISPONIVEIS = ["ag", "processo"]

DESCRIPTION = """
Automação Jira → Obsidian vault — ViasuperDev
─────────────────────────────────────────────
Exemplos:

  # Gera AG a partir de um ticket
  jira-to-vault AG-32021

  # Gera rascunho de processo
  jira-to-vault AG-32021 --tipo processo

  # Visualiza sem salvar no vault
  jira-to-vault AG-32021 --dry-run

  # Busca tickets em andamento do projeto AG
  jira-to-vault --search 'project = AG AND status = "Em Andamento"'
"""


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="jira-to-vault",
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
    )

    # Argumento principal — ticket ou busca (mutuamente exclusivos)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "ticket",
        nargs="?",
        metavar="TICKET",
        help="Chave do ticket Jira (ex: AG-32021)",
    )
    group.add_argument(
        "--search",
        metavar="JQL",
        help="Busca tickets via JQL e gera documentos para cada resultado",
    )

    parser.add_argument(
        "--tipo",
        choices=TIPOS_DISPONIVEIS,
        default="ag",
        help=f"Tipo de documento a gerar. Padrão: ag. Opções: {', '.join(TIPOS_DISPONIVEIS)}",
    )
    parser.add_argument(
        "--atualiza",
        metavar="PROC_ID",
        default=None,
        help="ID do processo existente a atualizar (ex: PROC-001). Só válido com --tipo processo.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exibe o documento gerado sem salvar no vault",
    )

    return parser


def handle_ticket(
    key:      str,
    tipo:     str,
    dry_run:  bool,
    client:   JiraClient,
    atualiza: str | None = None,
) -> int:
    """
    Processa um único ticket.
    Retorna 0 em sucesso, 1 em falha.
    """
    try:
        issue = client.get_issue(key)
    except JiraClientError as e:
        log.error("%s", e)
        return 1

    log.info("Ticket encontrado: [%s] %s", issue.key, issue.summary)
    log.info("Tipo: %s | Prioridade: %s | Responsável: %s",
             issue.issue_type, issue.priority, issue.assignee)

    try:
        if tipo == "ag":
            # AG usa o título do Jira diretamente — sem prompt
            parsed = parse_ag(issue, nome_rotina=issue.summary)
            path   = write_ag(issue, parsed, dry_run=dry_run)

        elif tipo == "processo":
            if atualiza:
                # Merge: não pergunta nome da rotina — o processo já existe
                parsed = parse_processo(issue)
                try:
                    existing = find_processo(atualiza)
                except FileNotFoundError as e:
                    log.error("%s", e)
                    return 1
                path = merge_processo(existing, issue, parsed, dry_run=dry_run)
            else:
                # Criação: pergunta o nome da rotina
                sugestao    = extract_nome_rotina(issue)
                nome_rotina = prompt_nome_rotina(sugestao) if not dry_run else sugestao
                parsed = parse_processo(issue, nome_rotina=nome_rotina)
                path   = write_processo(issue, parsed, dry_run=dry_run)

        else:
            log.error("Tipo '%s' ainda não implementado.", tipo)
            return 1

    except FileExistsError:
        return 1
    except Exception as e:
        log.error("Erro ao gerar documento: %s", e)
        log.debug("", exc_info=True)
        return 1

    if not dry_run:
        print(f"\n✅ Documento criado: {path}")
        vault_name = config.VAULT_ROOT.name
        file_rel   = path.relative_to(config.VAULT_ROOT)
        print(f"   Abrir no Obsidian: obsidian://open?vault={vault_name}&file={file_rel}")

    return 0


def main() -> None:
    setup_logging()
    parser = build_parser()
    args   = parser.parse_args()

    # Valida configuração antes de qualquer operação
    config.validate()

    client = JiraClient.from_config()

    # ── Modo busca JQL ────────────────────────────────────────────────────────
    if args.search:
        try:
            issues = client.search_issues(args.search)
        except JiraClientError as e:
            log.error("%s", e)
            sys.exit(1)

        if not issues:
            print("Nenhum ticket encontrado para a query informada.")
            sys.exit(0)

        print(f"\n{len(issues)} ticket(s) encontrado(s):\n")
        for issue in issues:
            print(f"  [{issue.key}] {issue.summary}")

        answer = input(f"\nGerar {args.tipo} para todos? (s/N): ").strip().lower()
        if answer != "s":
            print("Operação cancelada.")
            sys.exit(0)

        exit_codes = [
            handle_ticket(issue.key, args.tipo, args.dry_run, client)
            for issue in issues
        ]
        sys.exit(1 if any(c != 0 for c in exit_codes) else 0)

    # ── Modo ticket único ─────────────────────────────────────────────────────
    exit_code = handle_ticket(args.ticket, args.tipo, args.dry_run, client, atualiza=args.atualiza)
    sys.exit(exit_code)