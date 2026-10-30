import sqlite3
import unittest

from services import auth, minutas
from tests.base import DADOS, BancoTestCase


class TestMinutas(BancoTestCase):
    def test_criar_persiste_e_cria_cliente_e_processo(self):
        m = minutas.criar(self.c, self.est, DADOS)
        self.assertEqual((m["status"], m["versao"]), ("rascunho", 1))
        self.assertIn("**Processo:** 0001234-56.2026.8.16.0010", m["conteudo_md"])
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM cliente").fetchone()[0], 1)
        minutas.criar(self.c, self.est, DADOS)  # reaproveita cliente e processo
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM processo").fetchone()[0], 1)

    def test_validacao_de_campos(self):
        for ruim in ({}, {**DADOS, "fatos": "  "}, {**DADOS, "pedido": "x" * 5000}, {**DADOS, "cliente": 5}, "texto"):
            with self.assertRaises(minutas.ErroValidacao):
                minutas.criar(self.c, self.est, ruim)

    def test_sql_injection_e_tratado_como_texto(self):
        m = minutas.criar(self.c, self.est, {**DADOS, "cliente": "x'); DROP TABLE documento;--"})
        self.assertEqual(m["cliente"], "x'); DROP TABLE documento;--")

    def test_cliente_nao_acessa_minutas(self):
        with self.assertRaises(auth.ErroPermissao):
            minutas.listar(self.c, self.cli)

    def test_fluxo_completo_e_aprovacao_so_do_advogado(self):
        m = minutas.criar(self.c, self.est, DADOS)
        with self.assertRaises(minutas.ErroEstado):  # não pode aprovar sem passar pela revisão
            minutas.aprovar(self.c, self.adv, m["id"])
        minutas.enviar_para_revisao(self.c, self.est, m["id"])
        with self.assertRaises(auth.ErroPermissao):
            minutas.aprovar(self.c, self.est, m["id"])
        aprovada = minutas.aprovar(self.c, self.adv, m["id"])
        self.assertEqual((aprovada["status"], aprovada["revisor"]), ("aprovada", "Advogado Teste"))

    def test_devolucao_exige_motivo_e_permite_nova_versao(self):
        m = minutas.criar(self.c, self.est, DADOS)
        minutas.enviar_para_revisao(self.c, self.est, m["id"])
        with self.assertRaises(minutas.ErroValidacao):
            minutas.devolver(self.c, self.adv, m["id"], " ")
        d = minutas.devolver(self.c, self.adv, m["id"], "Ajustar o pedido.")
        self.assertEqual(d["motivo_devolucao"], "Ajustar o pedido.")
        v2 = minutas.nova_versao(self.c, self.est, m["id"])
        self.assertEqual((v2["versao"], v2["origem_id"], v2["status"]), (2, m["id"], "rascunho"))

    def test_aprovada_e_imutavel_na_regra_e_no_banco(self):
        m = minutas.criar(self.c, self.est, DADOS)
        minutas.enviar_para_revisao(self.c, self.est, m["id"])
        minutas.aprovar(self.c, self.adv, m["id"])
        with self.assertRaises(minutas.ErroEstado):
            minutas.editar(self.c, self.est, m["id"], DADOS)
        with self.assertRaises(sqlite3.DatabaseError):  # trigger: nem SQL direto altera
            self.c.execute("UPDATE documento SET conteudo_md = 'adulterado' WHERE id = ?", (m["id"],))

    def test_exportacao_marca_rascunho_e_aprovada(self):
        m = minutas.criar(self.c, self.est, DADOS)
        self.assertIn("RASCUNHO", minutas.markdown_para_exportacao(m))
        minutas.enviar_para_revisao(self.c, self.est, m["id"])
        a = minutas.aprovar(self.c, self.adv, m["id"])
        texto = minutas.markdown_para_exportacao(a)
        self.assertNotIn("RASCUNHO", texto)
        self.assertIn("Aprovada por Advogado Teste", texto)

    def test_auditoria_do_fluxo_nao_guarda_conteudo(self):
        m = minutas.criar(self.c, self.est, DADOS)
        minutas.enviar_para_revisao(self.c, self.est, m["id"])
        acoes = [l["acao"] for l in self.c.execute("SELECT acao FROM auditoria WHERE entidade = 'documento'")]
        self.assertEqual(acoes, ["minuta_criada", "minuta_enviada_revisao"])
        todo = " ".join(str(tuple(l)) for l in self.c.execute("SELECT * FROM auditoria"))
        self.assertNotIn("Fatos fictícios", todo)

    def test_contagens(self):
        minutas.criar(self.c, self.est, DADOS)
        self.assertEqual(minutas.contagens(self.c, self.adv)["rascunho"], 1)


if __name__ == "__main__":
    unittest.main()
