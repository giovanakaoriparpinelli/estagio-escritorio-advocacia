"""Serviço HTTP local (somente 127.0.0.1): API JSON, geração de DOCX e entrega do protótipo."""
from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.md_to_docx import convert  # noqa: E402
from services import auth, cadastros, minutas  # noqa: E402
from services.database import conectar  # noqa: E402

TEMPLATE = ROOT / "identidade-visual" / "modelo timbrado.docx"
PROTOTIPO = ROOT / "prototype"
DB_PADRAO = ROOT / "data" / "escritorio.db"
LIMITE_CORPO = 64 * 1024
ORIGENS_PERMITIDAS = {"null", "http://127.0.0.1:8765", "http://localhost:8765"}  # null = protótipo aberto via file://
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def gerar_docx(markdown: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="minuta-") as pasta:
        origem, destino = Path(pasta) / "minuta.md", Path(pasta) / "minuta.docx"
        origem.write_text(markdown, encoding="utf-8")
        convert(origem, TEMPLATE, destino)
        return destino.read_bytes()


class Resposta(Exception):
    def __init__(self, status: int, corpo: object = None, bruto: bytes | None = None,
                 tipo: str = "application/json", extras: dict | None = None):
        self.status, self.corpo, self.bruto, self.tipo, self.extras = status, corpo, bruto, tipo, extras or {}


def _rota(metodo: str, padrao: str):
    return metodo, re.compile(f"^{padrao}$")


class Handler(BaseHTTPRequestHandler):
    db_path: Path = DB_PADRAO
    server_version = "EscritorioLocal"

    # ---- infraestrutura ---------------------------------------------------------------
    def _cabecalhos_comuns(self) -> None:
        origem = self.headers.get("Origin")
        if origem in ORIGENS_PERMITIDAS:
            self.send_header("Access-Control-Allow-Origin", origem)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")

    def _enviar(self, r: Resposta) -> None:
        corpo = r.bruto if r.bruto is not None else (
            b"" if r.corpo is None else json.dumps(r.corpo, ensure_ascii=False).encode())
        self.send_response(r.status)
        self._cabecalhos_comuns()
        if corpo:
            self.send_header("Content-Type", r.tipo + ("; charset=utf-8" if r.tipo.startswith("application/json") else ""))
        for chave, valor in r.extras.items():
            self.send_header(chave, valor)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self) -> dict:
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho > LIMITE_CORPO:
            raise Resposta(413, {"erro": "Requisição grande demais."})
        if tamanho == 0:
            return {}
        try:
            dados = json.loads(self.rfile.read(tamanho))
        except (ValueError, UnicodeDecodeError):
            raise Resposta(400, {"erro": "JSON inválido."}) from None
        if not isinstance(dados, dict):
            raise Resposta(400, {"erro": "Esperado um objeto JSON."})
        return dados

    def _token(self) -> str | None:
        cabecalho = self.headers.get("Authorization", "")
        return cabecalho[7:] if cabecalho.startswith("Bearer ") else None

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._enviar(Resposta(204))

    def do_GET(self) -> None:  # noqa: N802
        self._despachar("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._despachar("POST")

    def do_PUT(self) -> None:  # noqa: N802
        self._despachar("PUT")

    def _despachar(self, metodo: str) -> None:
        caminho = urlparse(self.path).path
        try:
            if not caminho.startswith("/api/"):
                if metodo != "GET":
                    raise Resposta(405, {"erro": "Método não permitido."})
                raise self._estatico(caminho)
            for (m, regex), funcao in ROTAS.items():
                achou = regex.match(caminho)
                if m == metodo and achou:
                    conexao = conectar(self.db_path)
                    try:
                        raise funcao(self, conexao, *achou.groups())
                    finally:
                        conexao.close()
            raise Resposta(404, {"erro": "Endpoint não encontrado."})
        except Resposta as r:
            self._enviar(r)
        except auth.ErroAutenticacao as e:
            self._enviar(Resposta(401, {"erro": str(e)}))
        except auth.ErroPermissao as e:
            self._enviar(Resposta(403, {"erro": str(e)}))
        except minutas.NaoEncontrado as e:
            self._enviar(Resposta(404, {"erro": str(e)}))
        except minutas.ErroEstado as e:
            self._enviar(Resposta(409, {"erro": str(e)}))
        except (minutas.ErroValidacao, ValueError) as e:
            self._enviar(Resposta(400, {"erro": str(e)}))
        except Exception:  # detalhes ficam fora da resposta e dos logs (podem conter dados da minuta)
            self.log_message("erro interno em %s %s", metodo, caminho)
            self._enviar(Resposta(500, {"erro": "Não foi possível concluir a operação."}))

    def _estatico(self, caminho: str) -> Resposta:
        nome = "index.html" if caminho in ("", "/") else caminho.lstrip("/")
        arquivo = (PROTOTIPO / nome).resolve()
        if PROTOTIPO.resolve() not in arquivo.parents or not arquivo.is_file():
            return Resposta(404, {"erro": "Arquivo não encontrado."})
        tipo = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
        return Resposta(200, bruto=arquivo.read_bytes(), tipo=tipo, extras={
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[document-service] {format % args}")


# ---- handlers das rotas (cada um devolve uma Resposta) -------------------------------------
def _usuario(h: Handler, c):
    return auth.usuario_da_sessao(c, h._token())


def login(h, c):
    dados = h._json()
    token, u = auth.autenticar(c, str(dados.get("email", "")), str(dados.get("senha", "")))
    return Resposta(200, {"token": token, "usuario": {"nome": u["nome"], "perfil": u["perfil"]}})


def logout(h, c):
    if h._token():
        auth.encerrar_sessao(c, h._token())
    return Resposta(204)


def eu(h, c):
    u = _usuario(h, c)
    return Resposta(200, {"nome": u["nome"], "perfil": u["perfil"]})


def painel(h, c):
    u = _usuario(h, c)
    return Resposta(200, {"minutas": minutas.contagens(c, u), "prazos": cadastros.prazos_proximos(c, u, 15)})


def listar_minutas(h, c):
    return Resposta(200, minutas.listar(c, _usuario(h, c)))


def criar_minuta(h, c):
    return Resposta(201, minutas.criar(c, _usuario(h, c), h._json()))


def obter_minuta(h, c, i):
    return Resposta(200, minutas.obter(c, _usuario(h, c), int(i)))


def editar_minuta(h, c, i):
    return Resposta(200, minutas.editar(c, _usuario(h, c), int(i), h._json()))


def enviar_revisao(h, c, i):
    return Resposta(200, minutas.enviar_para_revisao(c, _usuario(h, c), int(i)))


def aprovar_minuta(h, c, i):
    return Resposta(200, minutas.aprovar(c, _usuario(h, c), int(i)))


def devolver_minuta(h, c, i):
    return Resposta(200, minutas.devolver(c, _usuario(h, c), int(i), h._json().get("motivo")))


def versao_minuta(h, c, i):
    return Resposta(201, minutas.nova_versao(c, _usuario(h, c), int(i)))


def docx_minuta(h, c, i):
    u = _usuario(h, c)
    minuta = minutas.obter(c, u, int(i))
    from services.database import registrar_auditoria
    registrar_auditoria(c, u["id"], "docx_gerado", "documento", minuta["id"], f"status={minuta['status']}")
    return Resposta(200, bruto=gerar_docx(minutas.markdown_para_exportacao(minuta)), tipo=DOCX_MIME, extras={
        "Content-Disposition": f'attachment; filename="manifestacao-simples-{minuta["id"]}-v{minuta["versao"]}.docx"'})


def auditoria(h, c):
    u = _usuario(h, c)
    auth.exigir_perfil(u, "advogado")
    linhas = c.execute(
        "SELECT a.id, a.criado_em, a.acao, a.entidade, a.entidade_id, a.detalhe, u.nome AS usuario "
        "FROM auditoria a LEFT JOIN usuario u ON u.id = a.usuario_id ORDER BY a.id DESC LIMIT 100")
    return Resposta(200, [dict(l) for l in linhas])


def clientes(h, c):
    return Resposta(200, cadastros.listar_clientes(c, _usuario(h, c)))


def novo_cliente(h, c):
    return Resposta(201, cadastros.criar_cliente(c, _usuario(h, c), h._json()))


def processos(h, c):
    return Resposta(200, cadastros.listar_processos(c, _usuario(h, c)))


def novo_processo(h, c):
    return Resposta(201, cadastros.criar_processo(c, _usuario(h, c), h._json()))


def novo_prazo(h, c):
    return Resposta(201, cadastros.criar_prazo(c, _usuario(h, c), h._json()))


def prazo_cumprido(h, c, i):
    cadastros.marcar_prazo_cumprido(c, _usuario(h, c), int(i))
    return Resposta(204)


def docx_avulso(h, c):
    """Endpoint original da semana 6, mantido por compatibilidade; agora exige login."""
    _usuario(h, c)
    d = minutas.validar_dados(h._json())
    texto = minutas.montar_markdown(d) + "\n---\n\n> RASCUNHO — não aprovado pelo advogado. Revisão obrigatória.\n"
    return Resposta(200, bruto=gerar_docx(texto), tipo=DOCX_MIME, extras={
        "Content-Disposition": 'attachment; filename="manifestacao-simples.docx"'})


ROTAS = {
    _rota("POST", "/api/login"): login,
    _rota("POST", "/api/logout"): logout,
    _rota("GET", "/api/me"): eu,
    _rota("GET", "/api/painel"): painel,
    _rota("GET", "/api/minutas"): listar_minutas,
    _rota("POST", "/api/minutas"): criar_minuta,
    _rota("POST", "/api/minutas/docx"): docx_avulso,
    _rota("GET", r"/api/minutas/(\d+)"): obter_minuta,
    _rota("PUT", r"/api/minutas/(\d+)"): editar_minuta,
    _rota("POST", r"/api/minutas/(\d+)/enviar-revisao"): enviar_revisao,
    _rota("POST", r"/api/minutas/(\d+)/aprovar"): aprovar_minuta,
    _rota("POST", r"/api/minutas/(\d+)/devolver"): devolver_minuta,
    _rota("POST", r"/api/minutas/(\d+)/nova-versao"): versao_minuta,
    _rota("GET", r"/api/minutas/(\d+)/docx"): docx_minuta,
    _rota("GET", "/api/auditoria"): auditoria,
    _rota("GET", "/api/clientes"): clientes,
    _rota("POST", "/api/clientes"): novo_cliente,
    _rota("GET", "/api/processos"): processos,
    _rota("POST", "/api/processos"): novo_processo,
    _rota("POST", "/api/prazos"): novo_prazo,
    _rota("POST", r"/api/prazos/(\d+)/cumprido"): prazo_cumprido,
}


def criar_servidor(db_path: str | Path = DB_PADRAO, porta: int = 8765) -> ThreadingHTTPServer:
    """Servidor restrito ao loopback. `porta=0` escolhe uma porta livre (usado nos testes)."""
    classe = type("HandlerConfigurado", (Handler,), {"db_path": Path(db_path)})
    conectar(db_path).close()  # cria/migra o banco antes de aceitar requisições
    return ThreadingHTTPServer(("127.0.0.1", porta), classe)


if __name__ == "__main__":
    servidor = criar_servidor(os.environ.get("ESTAGIO_DB", DB_PADRAO))
    print("Serviço local em http://127.0.0.1:8765  (Ctrl+C para encerrar)")
    servidor.serve_forever()
