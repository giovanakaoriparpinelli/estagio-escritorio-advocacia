"""Backup consistente do banco SQLite, com verificação de integridade e rotação."""
from __future__ import annotations

import argparse
import os
from contextlib import closing
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def fazer_backup(origem: Path, pasta: Path, manter: int = 14) -> Path:
    if not origem.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {origem}")
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{origem.stem}-{datetime.now():%Y%m%d-%H%M%S}.db"
    with closing(sqlite3.connect(origem)) as de, closing(sqlite3.connect(destino)) as para:
        de.backup(para)  # API de backup online: seguro mesmo com o serviço em uso
    with closing(sqlite3.connect(destino)) as verificacao:
        resultado = verificacao.execute("PRAGMA integrity_check").fetchone()[0]
    if resultado != "ok":
        destino.unlink()
        raise RuntimeError(f"Backup corrompido ({resultado}); arquivo descartado.")
    for antigo in sorted(pasta.glob(f"{origem.stem}-*.db"))[:-manter]:
        antigo.unlink()
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(os.environ.get("ESTAGIO_DB", "data/escritorio.db")))
    parser.add_argument("--destino", type=Path, default=Path("data/backups"))
    parser.add_argument("--manter", type=int, default=14)
    args = parser.parse_args()
    try:
        print(f"Backup criado: {fazer_backup(args.db, args.destino, args.manter)}")
    except (OSError, RuntimeError) as erro:
        sys.exit(str(erro))


if __name__ == "__main__":
    main()
