import unittest

from services import auth
from tests.base import SENHA, BancoTestCase


class TestSenha(unittest.TestCase):
    def test_hash_verifica_e_nao_guarda_texto_puro(self):
        h = auth.hash_senha(SENHA, 1000)
        self.assertNotIn(SENHA, h)
        self.assertTrue(auth.verificar_senha(SENHA, h))
        self.assertFalse(auth.verificar_senha("outra", h))
        self.assertNotEqual(h, auth.hash_senha(SENHA, 1000))  # sal aleatório

    def test_hash_malformado_nao_autentica(self):
        self.assertFalse(auth.verificar_senha(SENHA, "lixo"))

    def test_politica_de_senha(self):
        for fraca in ("curta1", "somenteletrasaqui", "12345678901"):
            with self.assertRaises(ValueError):
                auth.validar_politica_senha(fraca)


class TestSessao(BancoTestCase):
    def test_login_valido_e_sessao(self):
        token, u = auth.autenticar(self.c, "ADV@exemplo.invalid", SENHA)
        self.assertEqual(auth.usuario_da_sessao(self.c, token)["id"], u["id"])
        armazenado = self.c.execute("SELECT token_hash FROM sessao").fetchone()[0]
        self.assertNotEqual(armazenado, token)  # só o hash do token é guardado

    def test_credenciais_invalidas_tem_mensagem_generica(self):
        with self.assertRaisesRegex(auth.ErroAutenticacao, "Credenciais inválidas"):
            auth.autenticar(self.c, "adv@exemplo.invalid", "errada")
        with self.assertRaisesRegex(auth.ErroAutenticacao, "Credenciais inválidas"):
            auth.autenticar(self.c, "ninguem@exemplo.invalid", SENHA)

    def test_bloqueio_apos_falhas_mesmo_com_senha_correta(self):
        for _ in range(auth.MAX_FALHAS):
            with self.assertRaises(auth.ErroAutenticacao):
                auth.autenticar(self.c, "adv@exemplo.invalid", "errada")
        with self.assertRaises(auth.ErroAutenticacao):
            auth.autenticar(self.c, "adv@exemplo.invalid", SENHA)

    def test_sessao_expirada_e_logout(self):
        token, _ = auth.autenticar(self.c, "adv@exemplo.invalid", SENHA)
        auth.encerrar_sessao(self.c, token)
        with self.assertRaises(auth.ErroAutenticacao):
            auth.usuario_da_sessao(self.c, token)
        token, _ = auth.autenticar(self.c, "adv@exemplo.invalid", SENHA)
        self.c.execute("UPDATE sessao SET expira_em = '2000-01-01 00:00:00'")
        with self.assertRaises(auth.ErroAutenticacao):
            auth.usuario_da_sessao(self.c, token)

    def test_usuario_inativo_nao_entra(self):
        self.c.execute("UPDATE usuario SET ativo = 0 WHERE email = 'est@exemplo.invalid'")
        with self.assertRaises(auth.ErroAutenticacao):
            auth.autenticar(self.c, "est@exemplo.invalid", SENHA)

    def test_eventos_de_login_sao_auditados_sem_senha(self):
        with self.assertRaises(auth.ErroAutenticacao):
            auth.autenticar(self.c, "adv@exemplo.invalid", "errada")
        auth.autenticar(self.c, "adv@exemplo.invalid", SENHA)
        textos = " ".join(str(tuple(l)) for l in self.c.execute("SELECT * FROM auditoria"))
        self.assertIn("login_falhou", textos)
        self.assertNotIn("errada", textos)
        self.assertNotIn(SENHA, textos)


if __name__ == "__main__":
    unittest.main()
