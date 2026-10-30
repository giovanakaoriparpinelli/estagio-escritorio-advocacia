"""Testes de ponta a ponta: servidor HTTP real em porta livre, banco temporário, dados fictícios."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from services import auth
from services.database import conectar
from services.document_service import criar_servidor
from tests.base import DADOS, SENHA


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.db = Path(cls.pasta.name) / "teste.db"
        c = conectar(cls.db)
        auth.cadastrar_usuario(c, "Advogado Teste", "adv@exemplo.invalid", "advogado", SENHA)
        auth.cadastrar_usuario(c, "Estagiária Teste", "est@exemplo.invalid", "estagiario", SENHA)
        c.close()
        cls.servidor = criar_servidor(cls.db, 0)
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        try:
            cls.pasta.cleanup()
        except OSError:
            pass

    def req(self, metodo, caminho, corpo=None, token=None):
        dados = json.dumps(corpo).encode() if corpo is not None else None
        r = urllib.request.Request(self.base + caminho, data=dados, method=metodo)
        r.add_header("Content-Type", "application/json")
        if token:
            r.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(r) as resp:
                bruto = resp.read()
                tipo = resp.headers.get("Content-Type", "")
                return resp.status, (json.loads(bruto) if "json" in tipo else bruto)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def login(self, email):
        status, corpo = self.req("POST", "/api/login", {"email": email, "senha": SENHA})
        self.assertEqual(status, 200)
        return corpo["token"]

    def test_rotas_exigem_login(self):
        for metodo, caminho in (("GET", "/api/minutas"), ("GET", "/api/painel"), ("POST", "/api/minutas/docx"),
                                ("GET", "/api/auditoria")):
            self.assertEqual(self.req(metodo, caminho, {} if metodo == "POST" else None)[0], 401, caminho)

    def test_login_invalido(self):
        status, corpo = self.req("POST", "/api/login", {"email": "adv@exemplo.invalid", "senha": "errada"})
        self.assertEqual((status, corpo["erro"]), (401, "Credenciais inválidas."))

    def test_fluxo_de_ponta_a_ponta(self):
        est, adv = self.login("est@exemplo.invalid"), self.login("adv@exemplo.invalid")
        status, m = self.req("POST", "/api/minutas", DADOS, est)
        self.assertEqual(status, 201)
        mid = m["id"]
        self.assertEqual(self.req("POST", f"/api/minutas/{mid}/aprovar", {}, adv)[0], 409)
        self.assertEqual(self.req("POST", f"/api/minutas/{mid}/enviar-revisao", {}, est)[1]["status"], "em_revisao")
        self.assertEqual(self.req("POST", f"/api/minutas/{mid}/aprovar", {}, est)[0], 403)
        self.assertEqual(self.req("POST", f"/api/minutas/{mid}/aprovar", {}, adv)[1]["status"], "aprovada")
        self.assertEqual(self.req("PUT", f"/api/minutas/{mid}", DADOS, est)[0], 409)
        status, docx = self.req("GET", f"/api/minutas/{mid}/docx", None, est)
        self.assertEqual(status, 200)
        self.assertTrue(docx.startswith(b"PK"))  # DOCX é um zip
        self.assertEqual(self.req("GET", "/api/auditoria", None, est)[0], 403)
        self.assertGreater(len(self.req("GET", "/api/auditoria", None, adv)[1]), 3)

    def test_entradas_invalidas(self):
        est = self.login("est@exemplo.invalid")
        self.assertEqual(self.req("POST", "/api/minutas", {"cliente": "x"}, est)[0], 400)
        self.assertEqual(self.req("GET", "/api/minutas/999999", None, est)[0], 404)
        self.assertEqual(self.req("GET", "/api/inexistente", None, est)[0], 404)

    def test_prototipo_e_bloqueio_de_path_traversal(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            self.assertIn(b"<html", resp.read())
        r = urllib.request.Request(self.base + "/..%2fservices/auth.py")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(r)
        self.assertEqual(ctx.exception.code, 404)

    def test_painel_e_cadastros(self):
        adv = self.login("adv@exemplo.invalid")
        s, cli = self.req("POST", "/api/clientes", {"nome": "Cliente API"}, adv)
        s2, proc = self.req("POST", "/api/processos", {"numero": "0004444-56.2026.8.16.0010", "cliente_id": cli["id"]}, adv)
        s3, _ = self.req("POST", "/api/prazos", {"processo_id": proc["id"], "data": "2099-01-01", "descricao": "x"}, adv)
        self.assertEqual((s, s2, s3), (201, 201, 201))
        status, painel = self.req("GET", "/api/painel", None, adv)
        self.assertEqual(status, 200)
        self.assertIn("rascunho", painel["minutas"])


if __name__ == "__main__":
    unittest.main()
