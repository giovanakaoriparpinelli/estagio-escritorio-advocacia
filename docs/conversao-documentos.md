# Conversão de documentos

Foi criada a ferramenta `scripts/md_to_docx.py` para converter os Markdown gerados pelo protótipo em DOCX baseado no arquivo `modelo timbrado.docx`.

## Uso

```powershell
python scripts/md_to_docx.py caminho\manifestacao-simples-rascunho.md --output documentos\manifestacao.docx
```

O modelo pode ser informado explicitamente:

```powershell
python scripts/md_to_docx.py rascunho.md --template "modelo timbrado.docx" --output documentos\manifestacao.docx
```

Esta primeira versão preserva o cabeçalho do modelo, adiciona o conteúdo após uma quebra de página e trata títulos, negrito, separadores e observações. A conversão para PDF ainda será uma etapa posterior.
