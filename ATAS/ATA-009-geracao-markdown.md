# ATA 009 — Geração real do Markdown

**Data:** 14/09/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 008

## Entrega realizada

O protótipo passou a gerar uma minuta Markdown real a partir do formulário de manifestação simples. O arquivo pode ser baixado localmente como `manifestacao-simples-rascunho.md`.

## Funcionamento

- validação dos campos obrigatórios pelo navegador;
- composição do Markdown com cliente, processo, finalidade, fatos e pedido;
- inclusão de data e hora de geração;
- aviso de que o texto é rascunho e exige revisão do advogado;
- download local do arquivo `.md`.

## Limitações atuais

- sem banco de dados;
- sem login real;
- sem salvamento permanente;
- sem conversão para DOCX/PDF;
- sem uso de API de IA;
- dados ainda devem ser fictícios.

## Validação solicitada

Abrir `prototype/index.html`, preencher o formulário com dados fictícios, clicar em “Gerar rascunho Markdown” e testar o download do arquivo.

## Próximo passo

Implementar a conversão do Markdown para DOCX usando o modelo timbrado, após confirmar as ferramentas disponíveis no ambiente local.
