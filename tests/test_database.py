import sqlite3
import unittest

from services.database import MIGRACOES, conectar, migrar
from tests.base import BancoTestCase


class TestEsquema(unittest.TestCase):
    def test_migracoes_sao_idempotentes(self):
        c = conectar(":memory:")
        self.assertEqual(c.execute("PRAGMA user_version").fetchone()[0], len(MIGRACOES))
        migrar(c)
        self.assertEqual(c.execute("PRAGMA user_version").fetchone()[0], len(MIGRACOES))

    def test_entidades_do_modelo_existem(self):
        c = conectar(":memory:")
        tabelas = {l[0] for l in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"usuario", "cliente", "processo", "prazo", "tarefa", "documento", "financeiro",
                         "sessao", "auditoria"} <= tabelas)


class TestIntegridade(BancoTestCase):
    def test_chave_estrangeira_impede_processo_sem_cliente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO processo (numero, cliente_id) VALUES ('x', 999)")

    def test_perfil_invalido_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO usuario (nome, email, perfil, senha_hash) VALUES ('a','b@c.d','root','x')")

    def test_numero_de_processo_unico(self):
        cid = self.c.execute("INSERT INTO cliente (nome) VALUES ('A')").lastrowid
        self.c.execute("INSERT INTO processo (numero, cliente_id) VALUES ('1', ?)", (cid,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO processo (numero, cliente_id) VALUES ('1', ?)", (cid,))

    def test_auditoria_nao_pode_ser_alterada_nem_apagada(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("UPDATE auditoria SET acao = 'x'")
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("DELETE FROM auditoria")


if __name__ == "__main__":
    unittest.main()
