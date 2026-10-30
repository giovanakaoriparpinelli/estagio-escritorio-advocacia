"""Popula um banco de DESENVOLVIMENTO com dados fictícios. Senhas aleatórias são exibidas uma única vez."""
from __future__ import annotations

import argparse
import secrets
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services import auth, cadastros, minutas  # noqa: E402
from services.database import conectar  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/dev.db")
    args = parser.parse_args()
    c = conectar(args.db)
    if c.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]:
        sys.exit("O banco já possui usuários; use um arquivo novo.")
    senhas = {}
    for nome, email, perfil in (("Advogado Teste", "advogado@exemplo.invalid", "advogado"),
                                ("Estagiária Teste", "estagiaria@exemplo.invalid", "estagiario")):
        senhas[email] = "Dev" + secrets.token_urlsafe(9) + "7"
        auth.cadastrar_usuario(c, nome, email, perfil, senhas[email])
    adv = c.execute("SELECT * FROM usuario WHERE perfil = 'advogado'").fetchone()
    for i in range(1, 6):
        cli = cadastros.criar_cliente(c, adv, {"nome": f"Cliente Fictício {i}"})
        proc = cadastros.criar_processo(c, adv, {"numero": f"000{i}234-56.2026.8.16.00{i}0", "cliente_id": cli["id"],
                                                 "assunto": "Assunto fictício"})
        cadastros.criar_prazo(c, adv, {"processo_id": proc["id"], "descricao": "Prazo fictício",
                                       "data": (date.today() + timedelta(days=3 * i)).isoformat()})
    minutas.criar(c, adv, {"cliente": "Cliente Fictício 1", "processo": "0001234-56.2026.8.16.0010",
                           "finalidade": "Exemplo", "fatos": "Fatos fictícios.", "pedido": "Pedido fictício."})
    print("Banco de desenvolvimento criado. Credenciais (anote agora):")
    for email, senha in senhas.items():
        print(f"  {email}  {senha}")


if __name__ == "__main__":
    main()
