"""Persistência local em SQLite, com migrações versionadas.

O esquema segue `docs/modelo-de-dados.md`. Cada item de MIGRACOES corresponde a uma
versão do esquema (PRAGMA user_version); novas versões nunca alteram as anteriores.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

FORMATO_DATA = "%Y-%m-%d %H:%M:%S"  # mesmo formato de datetime('now') do SQLite (UTC)

# --- v1: entidades do domínio (semana 8) -------------------------------------------------
_V1 = """
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    perfil TEXT NOT NULL CHECK (perfil IN ('advogado', 'estagiario', 'cliente')),
    senha_hash TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);
CREATE TABLE cliente (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    cpf_cnpj TEXT,
    contato TEXT,
    criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_cliente_nome ON cliente (nome COLLATE NOCASE);
CREATE TABLE processo (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL UNIQUE,
    cliente_id INTEGER NOT NULL REFERENCES cliente (id),
    vara TEXT,
    assunto TEXT,
    status TEXT NOT NULL DEFAULT 'ativo'
);
CREATE INDEX ix_processo_cliente ON processo (cliente_id);
CREATE TABLE prazo (
    id INTEGER PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processo (id),
    data TEXT NOT NULL,
    descricao TEXT NOT NULL,
    cumprido INTEGER NOT NULL DEFAULT 0 CHECK (cumprido IN (0, 1))
);
CREATE INDEX ix_prazo_processo ON prazo (processo_id, data);
CREATE TABLE tarefa (
    id INTEGER PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processo (id),
    responsavel_id INTEGER REFERENCES usuario (id),
    titulo TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'concluida')),
    data_limite TEXT
);
CREATE INDEX ix_tarefa_processo ON tarefa (processo_id);
CREATE TABLE documento (
    id INTEGER PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processo (id),
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    arquivo TEXT,
    versao INTEGER NOT NULL DEFAULT 1 CHECK (versao >= 1),
    origem_id INTEGER REFERENCES documento (id),
    campos_json TEXT,
    conteudo_md TEXT,
    criado_por INTEGER NOT NULL REFERENCES usuario (id),
    criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_documento_processo ON documento (processo_id, tipo, versao);
CREATE TABLE financeiro (
    id INTEGER PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processo (id),
    tipo TEXT NOT NULL CHECK (tipo IN ('honorario', 'custas')),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    vencimento TEXT NOT NULL,
    pago INTEGER NOT NULL DEFAULT 0 CHECK (pago IN (0, 1))
);
CREATE INDEX ix_financeiro_processo ON financeiro (processo_id);
"""

# --- v2: autenticação e trilha de auditoria (semana 9) -----------------------------------
_V2 = """
ALTER TABLE usuario ADD COLUMN tentativas_falhas INTEGER NOT NULL DEFAULT 0;
ALTER TABLE usuario ADD COLUMN bloqueado_ate TEXT;
CREATE TABLE sessao (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario (id),
    token_hash TEXT NOT NULL UNIQUE,
    criada_em TEXT NOT NULL,
    expira_em TEXT NOT NULL
);
CREATE INDEX ix_sessao_usuario ON sessao (usuario_id);
CREATE TABLE auditoria (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario (id),
    acao TEXT NOT NULL,
    entidade TEXT,
    entidade_id INTEGER,
    detalhe TEXT,
    criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_auditoria_entidade ON auditoria (entidade, entidade_id);
CREATE TRIGGER auditoria_sem_update BEFORE UPDATE ON auditoria
BEGIN SELECT RAISE(ABORT, 'A trilha de auditoria não pode ser alterada'); END;
CREATE TRIGGER auditoria_sem_delete BEFORE DELETE ON auditoria
BEGIN SELECT RAISE(ABORT, 'A trilha de auditoria não pode ser apagada'); END;
"""

# --- v3: fluxo de revisão e aprovação das minutas (semana 10) ----------------------------
_V3 = """
ALTER TABLE documento ADD COLUMN status TEXT NOT NULL DEFAULT 'rascunho'
    CHECK (status IN ('rascunho', 'em_revisao', 'aprovada', 'devolvida'));
ALTER TABLE documento ADD COLUMN revisado_por INTEGER REFERENCES usuario (id);
ALTER TABLE documento ADD COLUMN revisado_em TEXT;
ALTER TABLE documento ADD COLUMN motivo_devolucao TEXT;
CREATE INDEX ix_documento_status ON documento (status);
CREATE TRIGGER documento_aprovado_imutavel BEFORE UPDATE OF titulo, conteudo_md, campos_json ON documento
WHEN OLD.status = 'aprovada'
BEGIN SELECT RAISE(ABORT, 'Documento aprovado não pode ser alterado'); END;
"""

MIGRACOES: tuple[str, ...] = (_V1, _V2, _V3)


def agora(deslocamento: timedelta = timedelta(0)) -> str:
    """Data/hora UTC no formato do banco, opcionalmente deslocada."""
    return (datetime.now(timezone.utc) + deslocamento).strftime(FORMATO_DATA)


def migrar(conexao: sqlite3.Connection) -> int:
    """Aplica as migrações pendentes, cada uma em uma transação. Retorna a versão final."""
    atual = conexao.execute("PRAGMA user_version").fetchone()[0]
    for versao, script in enumerate(MIGRACOES, start=1):
        if versao <= atual:
            continue
        try:
            conexao.executescript(f"BEGIN;\n{script}\nPRAGMA user_version = {versao};\nCOMMIT;")
        except sqlite3.Error:
            if conexao.in_transaction:
                conexao.execute("ROLLBACK")
            raise
    return len(MIGRACOES)


def conectar(caminho: str | Path = ":memory:") -> sqlite3.Connection:
    """Abre (e migra) o banco. Use uma conexão por requisição/thread."""
    if str(caminho) != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(str(caminho), isolation_level=None)  # transações explícitas
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    migrar(conexao)
    return conexao


def registrar_auditoria(conexao: sqlite3.Connection, usuario_id: int | None, acao: str,
                        entidade: str | None = None, entidade_id: int | None = None,
                        detalhe: str | None = None) -> None:
    """Grava um evento. O detalhe nunca deve conter dados pessoais ou texto de minutas."""
    conexao.execute(
        "INSERT INTO auditoria (usuario_id, acao, entidade, entidade_id, detalhe, criado_em) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, acao, entidade, entidade_id, detalhe, agora()),
    )
