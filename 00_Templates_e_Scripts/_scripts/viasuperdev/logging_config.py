"""
logging_config.py — Inicialização do logging.

Separado do config.py para poder ser importado antes de qualquer
outro módulo, garantindo que todos os logs sejam capturados desde
o início da execução.

Uso:
    # Primeiro import em qualquer entry point
    from viasuperdev.logging_config import setup_logging
    setup_logging()
"""

from __future__ import annotations

import logging
import os
import sys


def setup_logging(level: str | None = None) -> None:
    """
    Configura o logging global da aplicação.

    Deve ser chamado uma única vez, no início do entry point,
    antes de qualquer outro import do pacote viasuperdev.

    Args:
        level: nível de log (DEBUG/INFO/WARNING/ERROR).
               Se None, lê de LOG_LEVEL no ambiente ou usa INFO.
    """
    # Se já foi configurado com o mesmo nível, não reconfigura
    raw_level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric   = getattr(logging, raw_level.upper(), logging.INFO)
    if logging.root.handlers and logging.root.level == numeric:
        return

    logging.basicConfig(
        level=numeric,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )