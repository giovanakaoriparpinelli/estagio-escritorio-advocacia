"""Cadastros de clientes, processos e prazos (acesso restrito aos perfis internos)."""
from __future__ import annotations

import re
import sqlite3
from datetime import date, timedelta

from services.auth import PERFIS_INTERNOS, exigir_perfil
from services.database import registrar_auditoria
from services.minutas import ErroValidacao, NaoEncontrado

_NUMERO_CNJ = re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$")


def _texto(dados: dict, campo: str, maximo: int, obrigatorio: bool = True) -> str | None:
    valor = dados.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
        return None
    if not isinstance(valor, str) or len(valor.strip()) > maximo:
        raise ErroValidacao(f"Valor inválido para '{campo}'.")
    return valor.strip()


def criar_cliente(conexao: sqlite3.Connection, usuario: sqlite3.Row, dados: dict) -> dict:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    nome = _texto(dados, "nome", 200)
    contato = _texto(dados, "contato", 200, obrigatorio=False)
    documento = _texto(dados, "cpf_cnpj", 20, obrigatorio=False)
    if documento and not re.fullmatch(r"[\d.\-/]{11,18}", documento):
        raise ErroValidacao("CPF/CNPJ em formato inválido.")
    cursor = conexao.execute("INSERT INTO cliente (nome, cpf_cnpj, contato) VALUES (?, ?, ?)", (nome, documento, contato))
    registrar_auditoria(conexao, usuario["id"], "cliente_criado", "cliente", cursor.lastrowid)
    return {"id": cursor.lastrowid, "nome": nome}


def criar_processo(conexao: sqlite3.Connection, usuario: sqlite3.Row, dados: dict) -> dict:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    numero = _texto(dados, "numero", 60)
    if not _NUMERO_CNJ.match(numero):
        raise ErroValidacao("Número fora do padrão CNJ (0000000-00.0000.0.00.0000).")
    cliente_id = dados.get("cliente_id")
    if not isinstance(cliente_id, int) or not conexao.execute("SELECT 1 FROM cliente WHERE id = ?", (cliente_id,)).fetchone():
        raise NaoEncontrado("Cliente não encontrado.")
    if conexao.execute("SELECT 1 FROM processo WHERE numero = ?", (numero,)).fetchone():
        raise ErroValidacao("Já existe um processo com este número.")
    cursor = conexao.execute(
        "INSERT INTO processo (numero, cliente_id, vara, assunto) VALUES (?, ?, ?, ?)",
        (numero, cliente_id, _texto(dados, "vara", 200, False), _texto(dados, "assunto", 300, False)))
    registrar_auditoria(conexao, usuario["id"], "processo_criado", "processo", cursor.lastrowid)
    return {"id": cursor.lastrowid, "numero": numero}


def criar_prazo(conexao: sqlite3.Connection, usuario: sqlite3.Row, dados: dict) -> dict:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    try:
        data = date.fromisoformat(str(dados.get("data", "")))
    except ValueError:
        raise ErroValidacao("Data inválida (use AAAA-MM-DD).") from None
    descricao = _texto(dados, "descricao", 300)
    processo_id = dados.get("processo_id")
    if not isinstance(processo_id, int) or not conexao.execute("SELECT 1 FROM processo WHERE id = ?", (processo_id,)).fetchone():
        raise NaoEncontrado("Processo não encontrado.")
    cursor = conexao.execute("INSERT INTO prazo (processo_id, data, descricao) VALUES (?, ?, ?)",
                             (processo_id, data.isoformat(), descricao))
    registrar_auditoria(conexao, usuario["id"], "prazo_criado", "prazo", cursor.lastrowid, f"data={data.isoformat()}")
    return {"id": cursor.lastrowid, "data": data.isoformat()}


def marcar_prazo_cumprido(conexao: sqlite3.Connection, usuario: sqlite3.Row, prazo_id: int) -> None:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    if conexao.execute("UPDATE prazo SET cumprido = 1 WHERE id = ?", (prazo_id,)).rowcount == 0:
        raise NaoEncontrado("Prazo não encontrado.")
    registrar_auditoria(conexao, usuario["id"], "prazo_cumprido", "prazo", prazo_id)


def prazos_proximos(conexao: sqlite3.Connection, usuario: sqlite3.Row, dias: int = 15,
                    hoje: date | None = None) -> list[dict]:
    """Prazos não cumpridos até `dias` à frente (inclui os já vencidos), do mais urgente ao menos."""
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    hoje = hoje or date.today()
    limite = (hoje + timedelta(days=dias)).isoformat()
    linhas = conexao.execute(
        "SELECT z.id, z.data, z.descricao, p.numero AS processo, c.nome AS cliente FROM prazo z "
        "JOIN processo p ON p.id = z.processo_id JOIN cliente c ON c.id = p.cliente_id "
        "WHERE z.cumprido = 0 AND z.data <= ? ORDER BY z.data, z.id", (limite,))
    resultado = []
    for linha in linhas:
        item = dict(linha)
        item["dias_restantes"] = (date.fromisoformat(item["data"]) - hoje).days
        item["vencido"] = item["dias_restantes"] < 0
        resultado.append(item)
    return resultado


def listar_clientes(conexao: sqlite3.Connection, usuario: sqlite3.Row) -> list[dict]:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    return [dict(l) for l in conexao.execute(
        "SELECT c.id, c.nome, COUNT(p.id) AS processos FROM cliente c LEFT JOIN processo p ON p.cliente_id = c.id "
        "GROUP BY c.id ORDER BY c.nome COLLATE NOCASE LIMIT 500")]


def listar_processos(conexao: sqlite3.Connection, usuario: sqlite3.Row) -> list[dict]:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    return [dict(l) for l in conexao.execute(
        "SELECT p.id, p.numero, p.vara, p.assunto, p.status, c.nome AS cliente FROM processo p "
        "JOIN cliente c ON c.id = p.cliente_id ORDER BY p.id DESC LIMIT 500")]
