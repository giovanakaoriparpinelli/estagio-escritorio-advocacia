"""Gera as versões HTML e PDF de uma ata a partir do arquivo Markdown em ATAS/.

Uso:
    python scripts/gerar_ata.py ATAS/ATA-016-*.md [outras atas...]

O PDF é produzido pelo Microsoft Edge em modo headless (já instalado no Windows).
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

import markdown

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

CSS = (
    "@page{size:A4;margin:22mm 18mm}"
    "body{font-family:Arial,sans-serif;color:#202124;font-size:11pt;line-height:1.45}"
    "h1{color:#17365d;font-size:20pt;border-bottom:2px solid #17365d;padding-bottom:8px}"
    "h2{color:#17365d;font-size:14pt;margin-top:20px}"
    "h3{color:#17365d;font-size:12pt}"
    ".meta{background:#eef3f8;border-left:4px solid #17365d;padding:10px 14px}"
    ".footer{margin-top:28px;font-size:9pt;color:#666;border-top:1px solid #ccc;padding-top:8px}"
    "pre{background:#f5f5f5;border:1px solid #ddd;border-radius:4px;padding:10px;"
    "font-family:Consolas,monospace;font-size:9pt;overflow-x:auto;white-space:pre-wrap}"
    "table{border-collapse:collapse;width:100%;font-size:10pt}"
    "th,td{border:1px solid #ccd;padding:4px 8px;text-align:left}th{background:#eef3f8}"
    "img{max-width:100%;margin:8px 0}"
)

RODAPE = ("Documento de acompanhamento do projeto. Não substitui documentos oficiais da UTFPR "
          "nem instrumentos jurídicos do escritório.")


def md_para_html(texto: str) -> tuple[str, str]:
    linhas = texto.lstrip("\ufeff").splitlines()
    titulo = linhas[0].removeprefix("# ").strip()
    meta: list[str] = []
    i = 1
    while i < len(linhas) and not linhas[i].strip():
        i += 1
    while i < len(linhas) and linhas[i].startswith("**"):
        meta.append(re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(linhas[i].strip(), quote=False)))
        i += 1
    corpo = markdown.markdown("\n".join(linhas[i:]), extensions=["fenced_code", "tables"])
    pagina = (
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
        f"<style>{CSS}</style></head><body><h1>{html.escape(titulo)}</h1>"
        f'<div class="meta">{"<br>".join(meta)}</div>{corpo}'
        f'<div class="footer">{RODAPE}</div></body></html>'
    )
    return titulo, pagina


def gerar(md_path: Path) -> None:
    _, pagina = md_para_html(md_path.read_text(encoding="utf-8"))
    html_path = md_path.with_suffix(".html")
    html_path.write_text(pagina, encoding="utf-8")
    pdf_path = md_path.with_suffix(".pdf")
    subprocess.run(
        [str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path.resolve()}", html_path.resolve().as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    print(f"ok: {html_path.name}, {pdf_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atas", nargs="+", type=Path)
    for caminho in parser.parse_args().atas:
        gerar(caminho)


if __name__ == "__main__":
    sys.exit(main())
