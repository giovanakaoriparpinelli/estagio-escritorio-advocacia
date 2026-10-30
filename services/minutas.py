"""Regras de negócio das minutas: validação, versionamento e fluxo de revisão/aprovação.

Fluxo:  rascunho -> em_revisao -> aprovada | devolvida;  devolvida/aprovada -> nova versão (rascunho).
Somente o perfil `advogado` aprova ou devolve. Aprovada é imutável (também garantido por trigger).
"""
from __future__ import annotations

import json
import sqlite3

from services.auth import ErroPermissao, PERFIS_INTERNOS, exigir_perfil
from services.database import agora, registrar_auditoria

TIPO = "manifestacao_simples"
CAMPOS = ("cliente", "processo", "finalidade", "fatos", "pedido")
LIMITES = {"cliente": 200, "processo": 60, "finalidade": 300, "fatos": 8000, "pedido": 4000}
ROTULO_STATUS = {"rascunho": "Rascunho", "em_revisao": "Em revisão", "aprovada": "Aprovada", "devolvida": "Devolvida"}


class ErroValidacao(ValueError):
    pass


class ErroEstado(Exception):
    """Operação incompatível com o status atual da minuta."""


class NaoEncontrado(LookupError):
    pass


def validar_dados(dados: object) -> dict[str, str]:
    if not isinstance(dados, dict):
        raise ErroValidacao("Dados inválidos.")
    limpos: dict[str, str] = {}
    for campo in CAMPOS:
        valor = dados.get(campo, "")
        if not isinstance(valor, str) or not valor.strip():
            raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
        valor = valor.strip()
        if len(valor) > LIMITES[campo]:
            raise ErroValidacao(f"O campo '{campo}' excede {LIMITES[campo]} caracteres.")
        limpos[campo] = valor
    return limpos


def montar_markdown(d: dict[str, str]) -> str:
    return (f"# Manifestação simples\n\n**Cliente/parte representada:** {d['cliente']}  \n"
            f"**Processo:** {d['processo']}\n\n## Finalidade\n\n{d['finalidade']}\n\n"
            f"## Fatos e informações\n\n{d['fatos']}\n\n## Pedido ou providência\n\n{d['pedido']}\n")


def markdown_para_exportacao(minuta: dict) -> str:
    """Acrescenta a marca de status; só a minuta aprovada perde o aviso de rascunho."""
    if minuta["status"] == "aprovada":
        rodape = f"> Aprovada por {minuta['revisor']} em {minuta['revisado_em']} (UTC)."
    else:
        rodape = f"> RASCUNHO ({ROTULO_STATUS[minuta['status']]}) — não aprovado pelo advogado. Revisão obrigatória."
    return f"{minuta['conteudo_md']}\n---\n\n{rodape}\n"


_SELECT = (
    "SELECT d.id, d.titulo, d.tipo, d.versao, d.origem_id, d.status, d.conteudo_md, d.campos_json, d.criado_em, "
    "d.revisado_em, d.motivo_devolucao, d.criado_por, c.nome AS cliente, p.numero AS processo, "
    "a.nome AS autor, r.nome AS revisor "
    "FROM documento d JOIN processo p ON p.id = d.processo_id JOIN cliente c ON c.id = p.cliente_id "
    "JOIN usuario a ON a.id = d.criado_por LEFT JOIN usuario r ON r.id = d.revisado_por "
)


def _para_dict(linha: sqlite3.Row, completo: bool) -> dict:
    item = dict(linha)
    campos = json.loads(item.pop("campos_json") or "{}")
    if completo:
        item["campos"] = campos
    else:
        item.pop("conteudo_md")
    return item


def obter(conexao: sqlite3.Connection, usuario: sqlite3.Row, minuta_id: int) -> dict:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    linha = conexao.execute(_SELECT + "WHERE d.id = ? AND d.tipo = ?", (minuta_id, TIPO)).fetchone()
    if linha is None:
        raise NaoEncontrado("Minuta não encontrada.")
    return _para_dict(linha, completo=True)


def listar(conexao: sqlite3.Connection, usuario: sqlite3.Row, status: str | None = None) -> list[dict]:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    filtro, args = ("AND d.status = ? ", (status,)) if status else ("", ())
    linhas = conexao.execute(_SELECT + f"WHERE d.tipo = ? {filtro}ORDER BY d.id DESC LIMIT 200", (TIPO, *args))
    return [_para_dict(l, completo=False) for l in linhas]


def contagens(conexao: sqlite3.Connection, usuario: sqlite3.Row) -> dict[str, int]:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    base = {s: 0 for s in ROTULO_STATUS}
    for linha in conexao.execute("SELECT status, COUNT(*) AS n FROM documento WHERE tipo = ? GROUP BY status", (TIPO,)):
        base[linha["status"]] = linha["n"]
    return base


def _processo_id(conexao: sqlite3.Connection, nome_cliente: str, numero: str) -> int:
    processo = conexao.execute("SELECT id, cliente_id FROM processo WHERE numero = ?", (numero,)).fetchone()
    if processo:
        return processo["id"]
    cliente = conexao.execute("SELECT id FROM cliente WHERE nome = ? COLLATE NOCASE", (nome_cliente,)).fetchone()
    cliente_id = cliente["id"] if cliente else conexao.execute(
        "INSERT INTO cliente (nome) VALUES (?)", (nome_cliente,)).lastrowid
    return conexao.execute("INSERT INTO processo (numero, cliente_id) VALUES (?, ?)", (numero, cliente_id)).lastrowid


def _inserir(conexao, usuario, dados, versao, origem_id) -> int:
    processo_id = _processo_id(conexao, dados["cliente"], dados["processo"])
    cursor = conexao.execute(
        "INSERT INTO documento (processo_id, tipo, titulo, versao, origem_id, campos_json, conteudo_md, criado_por, criado_em) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (processo_id, TIPO, f"Manifestação simples — {dados['finalidade'][:80]}", versao, origem_id,
         json.dumps(dados, ensure_ascii=False), montar_markdown(dados), usuario["id"], agora()))
    return cursor.lastrowid


def criar(conexao: sqlite3.Connection, usuario: sqlite3.Row, dados: object) -> dict:
    exigir_perfil(usuario, *PERFIS_INTERNOS)
    limpos = validar_dados(dados)
    conexao.execute("BEGIN")
    try:
        minuta_id = _inserir(conexao, usuario, limpos, 1, None)
        registrar_auditoria(conexao, usuario["id"], "minuta_criada", "documento", minuta_id, "versao=1")
        conexao.execute("COMMIT")
    except Exception:
        conexao.execute("ROLLBACK")
        raise
    return obter(conexao, usuario, minuta_id)


def _carregar(conexao, usuario, minuta_id) -> dict:
    return obter(conexao, usuario, minuta_id)


def editar(conexao: sqlite3.Connection, usuario: sqlite3.Row, minuta_id: int, dados: object) -> dict:
    minuta = _carregar(conexao, usuario, minuta_id)
    if minuta["status"] != "rascunho":
        raise ErroEstado("Somente rascunhos podem ser editados; crie uma nova versão.")
    limpos = validar_dados(dados)
    processo_id = _processo_id(conexao, limpos["cliente"], limpos["processo"])
    with _transacao(conexao):
        conexao.execute(
            "UPDATE documento SET processo_id = ?, titulo = ?, campos_json = ?, conteudo_md = ? WHERE id = ?",
            (processo_id, f"Manifestação simples — {limpos['finalidade'][:80]}",
             json.dumps(limpos, ensure_ascii=False), montar_markdown(limpos), minuta_id))
        registrar_auditoria(conexao, usuario["id"], "minuta_editada", "documento", minuta_id)
    return obter(conexao, usuario, minuta_id)


class _transacao:
    def __init__(self, conexao): self.c = conexao
    def __enter__(self): self.c.execute("BEGIN")
    def __exit__(self, tipo, *_):
        self.c.execute("ROLLBACK" if tipo else "COMMIT")


def _mudar_status(conexao, usuario, minuta_id, de: tuple[str, ...], para: str, acao: str,
                  revisao: bool = False, motivo: str | None = None) -> dict:
    minuta = _carregar(conexao, usuario, minuta_id)
    if minuta["status"] not in de:
        raise ErroEstado(f"Operação inválida para uma minuta {ROTULO_STATUS[minuta['status']].lower()}.")
    with _transacao(conexao):
        if revisao:
            conexao.execute(
                "UPDATE documento SET status = ?, revisado_por = ?, revisado_em = ?, motivo_devolucao = ? WHERE id = ?",
                (para, usuario["id"], agora(), motivo, minuta_id))
        else:
            conexao.execute("UPDATE documento SET status = ? WHERE id = ?", (para, minuta_id))
        registrar_auditoria(conexao, usuario["id"], acao, "documento", minuta_id, f"{minuta['status']}->{para}")
    return obter(conexao, usuario, minuta_id)


def enviar_para_revisao(conexao, usuario, minuta_id) -> dict:
    return _mudar_status(conexao, usuario, minuta_id, ("rascunho",), "em_revisao", "minuta_enviada_revisao")


def aprovar(conexao, usuario, minuta_id) -> dict:
    exigir_perfil(usuario, "advogado")
    return _mudar_status(conexao, usuario, minuta_id, ("em_revisao",), "aprovada", "minuta_aprovada", revisao=True)


def devolver(conexao, usuario, minuta_id, motivo: object) -> dict:
    exigir_perfil(usuario, "advogado")
    if not isinstance(motivo, str) or not motivo.strip() or len(motivo) > 1000:
        raise ErroValidacao("Informe o motivo da devolução (até 1000 caracteres).")
    return _mudar_status(conexao, usuario, minuta_id, ("em_revisao",), "devolvida", "minuta_devolvida",
                         revisao=True, motivo=motivo.strip())


def nova_versao(conexao, usuario, minuta_id) -> dict:
    """Cria um novo rascunho a partir de uma minuta devolvida ou aprovada, preservando o histórico."""
    minuta = _carregar(conexao, usuario, minuta_id)
    if minuta["status"] not in ("devolvida", "aprovada"):
        raise ErroEstado("Só é possível versionar minutas devolvidas ou aprovadas.")
    ultima = conexao.execute(
        "SELECT MAX(d.versao) FROM documento d WHERE d.id = ? OR d.origem_id = ?", (minuta_id, minuta_id)).fetchone()[0]
    with _transacao(conexao):
        novo_id = _inserir(conexao, usuario, minuta["campos"], ultima + 1, minuta_id)
        registrar_auditoria(conexao, usuario["id"], "minuta_nova_versao", "documento", novo_id, f"origem={minuta_id}")
    return obter(conexao, usuario, novo_id)


__all__ = ["ErroPermissao"]
