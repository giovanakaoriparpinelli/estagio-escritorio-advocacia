"""Autenticação local: senhas com PBKDF2, sessões por token opaco e bloqueio por tentativas."""
from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import timedelta

from services.database import agora, registrar_auditoria

ITERACOES = 240_000
MAX_FALHAS = 5
BLOQUEIO = timedelta(minutes=15)
DURACAO_SESSAO = timedelta(hours=8)
PERFIS_INTERNOS = ("advogado", "estagiario")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErroAutenticacao(Exception):
    """Credenciais inválidas, conta bloqueada ou sessão expirada (mensagem genérica de propósito)."""


class ErroPermissao(Exception):
    """Usuário autenticado sem permissão para a operação."""


def hash_senha(senha: str, iteracoes: int | None = None) -> str:
    iteracoes = iteracoes or ITERACOES
    sal = secrets.token_bytes(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, iteracoes)
    return "pbkdf2_sha256${}${}${}".format(
        iteracoes, base64.b64encode(sal).decode(), base64.b64encode(resumo).decode())


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        algoritmo, iteracoes, sal, resumo = armazenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac("sha256", senha.encode(), base64.b64decode(sal), int(iteracoes))
        return hmac.compare_digest(calculado, base64.b64decode(resumo))
    except (ValueError, TypeError):
        return False


def validar_politica_senha(senha: str) -> None:
    if len(senha) < 10 or not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        raise ValueError("A senha deve ter ao menos 10 caracteres, com letras e números.")


def cadastrar_usuario(conexao: sqlite3.Connection, nome: str, email: str, perfil: str, senha: str) -> int:
    nome, email = nome.strip(), email.strip().lower()
    if not nome or not _EMAIL.match(email):
        raise ValueError("Nome e e-mail válidos são obrigatórios.")
    if perfil not in ("advogado", "estagiario", "cliente"):
        raise ValueError("Perfil inválido.")
    validar_politica_senha(senha)
    cursor = conexao.execute(
        "INSERT INTO usuario (nome, email, perfil, senha_hash) VALUES (?, ?, ?, ?)",
        (nome, email, perfil, hash_senha(senha)))
    registrar_auditoria(conexao, cursor.lastrowid, "usuario_criado", "usuario", cursor.lastrowid, f"perfil={perfil}")
    return cursor.lastrowid


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def autenticar(conexao: sqlite3.Connection, email: str, senha: str) -> tuple[str, sqlite3.Row]:
    """Valida as credenciais e abre uma sessão. Devolve (token, usuário)."""
    usuario = conexao.execute(
        "SELECT * FROM usuario WHERE email = ? AND ativo = 1", (email.strip().lower(),)).fetchone()
    if usuario is None:
        hash_senha(senha)  # gasta o mesmo tempo, para não revelar se o e-mail existe
        registrar_auditoria(conexao, None, "login_falhou", detalhe="usuario_desconhecido")
        raise ErroAutenticacao("Credenciais inválidas.")
    if usuario["bloqueado_ate"] and usuario["bloqueado_ate"] > agora():
        registrar_auditoria(conexao, usuario["id"], "login_bloqueado", "usuario", usuario["id"])
        raise ErroAutenticacao("Credenciais inválidas.")
    if not verificar_senha(senha, usuario["senha_hash"]):
        falhas = usuario["tentativas_falhas"] + 1
        bloqueio = agora(BLOQUEIO) if falhas >= MAX_FALHAS else None
        conexao.execute("UPDATE usuario SET tentativas_falhas = ?, bloqueado_ate = ? WHERE id = ?",
                        (0 if bloqueio else falhas, bloqueio, usuario["id"]))
        registrar_auditoria(conexao, usuario["id"], "login_falhou", "usuario", usuario["id"],
                            "conta_bloqueada" if bloqueio else f"tentativa={falhas}")
        raise ErroAutenticacao("Credenciais inválidas.")
    token = secrets.token_urlsafe(32)
    conexao.execute("UPDATE usuario SET tentativas_falhas = 0, bloqueado_ate = NULL WHERE id = ?", (usuario["id"],))
    conexao.execute("DELETE FROM sessao WHERE expira_em <= ?", (agora(),))
    conexao.execute(
        "INSERT INTO sessao (usuario_id, token_hash, criada_em, expira_em) VALUES (?, ?, ?, ?)",
        (usuario["id"], _hash_token(token), agora(), agora(DURACAO_SESSAO)))
    registrar_auditoria(conexao, usuario["id"], "login", "usuario", usuario["id"])
    return token, usuario


def usuario_da_sessao(conexao: sqlite3.Connection, token: str | None) -> sqlite3.Row:
    """Resolve o token em usuário ativo ou levanta ErroAutenticacao."""
    if not token:
        raise ErroAutenticacao("Sessão ausente ou expirada.")
    usuario = conexao.execute(
        "SELECT u.* FROM sessao s JOIN usuario u ON u.id = s.usuario_id "
        "WHERE s.token_hash = ? AND s.expira_em > ? AND u.ativo = 1",
        (_hash_token(token), agora())).fetchone()
    if usuario is None:
        raise ErroAutenticacao("Sessão ausente ou expirada.")
    return usuario


def encerrar_sessao(conexao: sqlite3.Connection, token: str) -> None:
    sessao = conexao.execute("SELECT usuario_id FROM sessao WHERE token_hash = ?", (_hash_token(token),)).fetchone()
    conexao.execute("DELETE FROM sessao WHERE token_hash = ?", (_hash_token(token),))
    if sessao:
        registrar_auditoria(conexao, sessao["usuario_id"], "logout", "usuario", sessao["usuario_id"])


def exigir_perfil(usuario: sqlite3.Row, *perfis: str) -> None:
    if usuario["perfil"] not in perfis:
        raise ErroPermissao("Seu perfil não tem permissão para esta operação.")
