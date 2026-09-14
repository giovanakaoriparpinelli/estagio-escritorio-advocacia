"""Local standard-library HTTP service for generating DOCX from a draft."""
from __future__ import annotations

import json
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.md_to_docx import convert

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "modelo timbrado.docx"


class Handler(BaseHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/minutas/docx":
            self.send_error(404, "Endpoint não encontrado")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            required = ("cliente", "processo", "finalidade", "fatos", "pedido")
            if any(not str(payload.get(field, "")).strip() for field in required):
                self.send_error(400, "Campos obrigatórios ausentes")
                return
            markdown = (f"# Manifestação simples\n\n**Cliente/parte representada:** {payload['cliente']}  \n"
                        f"**Processo:** {payload['processo']}\n\n## Finalidade\n\n{payload['finalidade']}\n\n"
                        f"## Fatos e informações\n\n{payload['fatos']}\n\n## Pedido ou providência\n\n{payload['pedido']}\n")
            with tempfile.TemporaryDirectory(prefix="minuta-") as folder:
                base = Path(folder)
                source = base / "minuta.md"
                output = base / "manifestacao.docx"
                source.write_text(markdown, encoding="utf-8")
                convert(source, TEMPLATE, output)
                content = output.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            self.send_header("Content-Disposition", 'attachment; filename="manifestacao-simples.docx"')
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            self.send_error(400, f"Requisição inválida: {error}")
        except Exception as error:  # keep details out of the response
            self.send_error(500, "Não foi possível gerar o documento")

    def log_message(self, format: str, *args: object) -> None:
        print(f"[document-service] {format % args}")


if __name__ == "__main__":
    print("Serviço local em http://127.0.0.1:8765")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
