"""
test_logging_config.py — Testes unitários para logging_config.py.
"""

from __future__ import annotations

import logging


class TestSetupLogging:
    def setup_method(self):
        """Reseta estado completo do root logger antes de cada teste."""
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def teardown_method(self):
        """Garante reset mesmo se o teste falhar."""
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def test_configura_handler_no_root(self):
        from viasuperdev.logging_config import setup_logging
        setup_logging()
        assert len(logging.root.handlers) > 0

    def test_nivel_padrao_e_info(self):
        from viasuperdev.logging_config import setup_logging
        setup_logging()
        assert logging.root.level == logging.INFO

    def test_nivel_debug_quando_passado(self):
        from viasuperdev.logging_config import setup_logging
        setup_logging(level="DEBUG")
        assert logging.root.level == logging.DEBUG

    def test_chamada_dupla_nao_duplica_handlers(self):
        from viasuperdev.logging_config import setup_logging
        setup_logging()
        count_antes = len(logging.root.handlers)
        setup_logging()
        assert len(logging.root.handlers) == count_antes

    def test_nivel_invalido_usa_info_como_fallback(self):
        from viasuperdev.logging_config import setup_logging
        setup_logging(level="INVALIDO")
        assert logging.root.level == logging.INFO