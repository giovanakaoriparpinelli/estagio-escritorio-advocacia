import unittest
from datetime import date

from services import auth, cadastros
from services.minutas import ErroValidacao, NaoEncontrado
from tests.base import BancoTestCase

NUM = "0001234-56.2026.8.16.0010"


class TestCadastros(BancoTestCase):
    def setUp(self):
        super().setUp()
        self.cliente = cadastros.criar_cliente(self.c, self.adv, {"nome": "Cliente Fictício"})
        self.processo = cadastros.criar_processo(self.c, self.adv, {"numero": NUM, "cliente_id": self.cliente["id"]})

    def test_processo_valida_numero_cliente_e_duplicidade(self):
        with self.assertRaises(ErroValidacao):
            cadastros.criar_processo(self.c, self.adv, {"numero": "123", "cliente_id": self.cliente["id"]})
        with self.assertRaises(NaoEncontrado):
            cadastros.criar_processo(self.c, self.adv, {"numero": "0009999-56.2026.8.16.0010", "cliente_id": 99})
        with self.assertRaises(ErroValidacao):
            cadastros.criar_processo(self.c, self.adv, {"numero": NUM, "cliente_id": self.cliente["id"]})

    def test_cpf_cnpj_invalido(self):
        with self.assertRaises(ErroValidacao):
            cadastros.criar_cliente(self.c, self.adv, {"nome": "X", "cpf_cnpj": "abc"})

    def test_prazos_proximos_ordenados_e_com_vencidos(self):
        hoje = date(2026, 10, 20)
        for data, desc in (("2026-10-25", "B"), ("2026-10-18", "vencido"), ("2026-12-30", "longe")):
            cadastros.criar_prazo(self.c, self.adv, {"processo_id": self.processo["id"], "data": data, "descricao": desc})
        lista = cadastros.prazos_proximos(self.c, self.adv, 15, hoje)
        self.assertEqual([p["descricao"] for p in lista], ["vencido", "B"])
        self.assertTrue(lista[0]["vencido"])
        self.assertEqual(lista[1]["dias_restantes"], 5)

    def test_prazo_cumprido_sai_da_lista(self):
        p = cadastros.criar_prazo(self.c, self.adv, {"processo_id": self.processo["id"], "data": "2026-10-21", "descricao": "A"})
        cadastros.marcar_prazo_cumprido(self.c, self.est, p["id"])
        self.assertEqual(cadastros.prazos_proximos(self.c, self.adv, 15, date(2026, 10, 20)), [])

    def test_data_invalida_e_perfil_cliente(self):
        with self.assertRaises(ErroValidacao):
            cadastros.criar_prazo(self.c, self.adv, {"processo_id": self.processo["id"], "data": "31/02/2026", "descricao": "A"})
        with self.assertRaises(auth.ErroPermissao):
            cadastros.listar_processos(self.c, self.cli)


if __name__ == "__main__":
    unittest.main()
