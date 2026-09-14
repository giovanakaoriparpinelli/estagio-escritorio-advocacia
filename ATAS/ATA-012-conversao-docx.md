# ATA 012 — Primeira conversão Markdown para DOCX

**Data:** 24/08/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 011

## Verificação do ambiente

Foi confirmado que o ambiente possui Python 3.12.10 e a biblioteca `python-docx`. Não foi identificado Pandoc instalado e a biblioteca Markdown não é necessária para a primeira implementação.

## Entrega realizada

Foi criado `scripts/md_to_docx.py`, que:

- recebe um arquivo Markdown;
- usa `modelo timbrado.docx` como modelo;
- preserva o documento-base e seu cabeçalho;
- adiciona o conteúdo da minuta;
- trata títulos, negrito, separadores e observações;
- salva um novo arquivo DOCX sem alterar o modelo original.

## Limitações

- Ainda não há conversão automática para PDF.
- A formatação Markdown suportada é deliberadamente limitada.
- A integração com o site e a aprovação do advogado ainda não estão implementadas.
- O resultado deve ser revisado visualmente antes de qualquer uso jurídico.

## Próximo passo

Testar o DOCX gerado com uma minuta fictícia, revisar a fidelidade do timbre e depois implementar o fluxo de aprovação e PDF.

## Anexo técnico — lógica de programação (detalhado posteriormente)

Trecho de `scripts/md_to_docx.py` com a função central da conversão, explicada em detalhe em [`docs/logica-de-programacao.md`](../docs/logica-de-programacao.md):

```python
def convert(source: Path, template: Path, destination: Path) -> None:
    document = Document(template)
    document.add_page_break()
    for line in source.read_text(encoding="utf-8-sig").splitlines():
        add_markdown_line(document, line)
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            if not run.font.name:
                run.font.name = "Arial"
            if not run.font.size:
                run.font.size = Pt(11)
    destination.parent.mkdir(parents=True, exist_ok=True)
    document.save(destination)
```

A função abre o `modelo timbrado.docx` como base — preservando cabeçalho e logotipo automaticamente — insere uma quebra de página e percorre o Markdown linha por linha, delegando a `add_markdown_line()` o reconhecimento de títulos (`# `), seções (`## `), negrito (`**texto**`) e separadores (`---`), convertendo cada um no estilo equivalente do Word via `python-docx`.
