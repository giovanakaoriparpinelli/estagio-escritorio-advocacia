import tempfile
import unittest
from pathlib import Path

from scripts.backup_banco import fazer_backup
from services.database import conectar


class TestBackup(unittest.TestCase):
    def test_backup_valido_e_rotacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "escritorio.db"
            c = conectar(origem)
            c.execute("INSERT INTO cliente (nome) VALUES ('Fictício')")
            c.close()
            for _ in range(3):
                fazer_backup(origem, Path(pasta) / "bk", manter=2)
            restantes = list((Path(pasta) / "bk").glob("*.db"))
            self.assertLessEqual(len(restantes), 2)
            copia = conectar(restantes[0])
            self.assertEqual(copia.execute("SELECT nome FROM cliente").fetchone()[0], "Fictício")
            copia.close()

    def test_banco_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            fazer_backup(Path("nao-existe.db"), Path("x"))


if __name__ == "__main__":
    unittest.main()
