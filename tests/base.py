"""Utilitários compartilhados pelos testes (somente dados fictícios)."""
from __future__ import annotations

import unittest

from services import auth
from services.database import conectar

auth.ITERACOES = 1_000  # hash rápido só nos testes

SENHA = "SenhaTeste123"
DADOS = {"cliente": "Cliente Fictício", "processo": "0001234-56.2026.8.16.0010",
         "finalidade": "Juntada de documento", "fatos": "Fatos fictícios.", "pedido": "Pedido fictício."}


class BancoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.c = conectar(":memory:")
        self.adv = self.usuario("Advogado Teste", "adv@exemplo.invalid", "advogado")
        self.est = self.usuario("Estagiária Teste", "est@exemplo.invalid", "estagiario")
        self.cli = self.usuario("Cliente Teste", "cli@exemplo.invalid", "cliente")

    def usuario(self, nome, email, perfil):
        uid = auth.cadastrar_usuario(self.c, nome, email, perfil, SENHA)
        return self.c.execute("SELECT * FROM usuario WHERE id = ?", (uid,)).fetchone()
