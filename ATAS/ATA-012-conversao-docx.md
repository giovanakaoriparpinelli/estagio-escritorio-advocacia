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
