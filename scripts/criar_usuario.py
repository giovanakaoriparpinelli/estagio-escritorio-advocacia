"""Cria um usuário interno; a senha é lida de forma oculta (nunca como argumento)."""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.auth import cadastrar_usuario  # noqa: E402
from services.database import conectar  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--perfil", choices=("advogado", "estagiario"), required=True)
    parser.add_argument("--db", default=os.environ.get("ESTAGIO_DB", "data/escritorio.db"))
    args = parser.parse_args()
    senha = getpass.getpass("Senha: ")
    if senha != getpass.getpass("Repita a senha: "):
        sys.exit("As senhas não conferem.")
    conexao = conectar(args.db)
    try:
        print(f"Usuário criado (id {cadastrar_usuario(conexao, args.nome, args.email, args.perfil, senha)}).")
    except ValueError as erro:
        sys.exit(str(erro))


if __name__ == "__main__":
    main()
