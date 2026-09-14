# ATA 006 — Primeira implementação do protótipo navegável

**Data:** 14/09/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 005

## Entrega realizada

Foi criado o primeiro protótipo navegável em `prototype/`, contendo:

- painel visual do escritório;
- navegação para nova minuta e histórico;
- formulário de manifestação simples;
- validação dos campos principais;
- simulação de criação de rascunho;
- estados visuais de rascunho e revisão;
- aviso de que devem ser usados dados fictícios.

## Decisões técnicas

- O protótipo é estático e não usa banco de dados.
- O botão de geração apenas simula a criação; ainda não produz Markdown real.
- O layout usa uma paleta provisória inspirada no contexto institucional e deverá ser validado contra o DOCX timbrado.
- Não há autenticação real, persistência, conversão DOCX/PDF ou integração externa nesta etapa.

## Critério de validação

O contratante deve abrir `prototype/index.html` no navegador e avaliar identidade visual, organização das telas e campos da manifestação simples.

## Próximos passos

1. Contratante aprovar ou solicitar alterações no layout.
2. Confirmar o primeiro modelo de manifestação e seus campos obrigatórios.
3. Implementar geração real do Markdown.
4. Verificar bibliotecas Python e ferramentas disponíveis para conversão DOCX/PDF.
