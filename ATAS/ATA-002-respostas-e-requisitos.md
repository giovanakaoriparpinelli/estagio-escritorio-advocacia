# ATA 002 — Respostas e requisitos da automação de minutas

**Data:** 15/06/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 001

## Respostas registradas

- O modelo visual está no arquivo `modelo timbrado.docx`, localizado na raiz do projeto.
- O primeiro caso de uso será a criação de minutas para cumprimento de prazo.
- A busca/identificação poderá usar o nome do cliente e/ou o número do processo.
- O sistema deverá salvar as versões e os arquivos produzidos.
- O fluxo aprovado será: Markdown → DOCX com timbre → leitura e revisão do advogado → aprovação → PDF para protocolo.
- O sistema terá login e área restrita.
- O ambiente é local, com raiz em `C:\\inetpub\\wwwroot`.
- Já existem recursos em PHP, SQL e Python; a existência e adequação serão verificadas conforme a evolução.
- O estágio será sem remuneração, conforme informado pelo contratante.
- O critério de aceite da primeira entrega será a aprovação do contratante.
- Na primeira versão, os dados serão digitados manualmente pelo advogado.

## Decisões técnicas preliminares

1. O Markdown será mantido como fonte editável e rastreável da minuta.
2. DOCX e PDF serão artefatos derivados e também serão preservados.
3. A aprovação será uma etapa explícita, identificando usuário e momento.
4. O layout será desenvolvido primeiro com dados fictícios.
5. A integração com o sistema separado de prazos não entra no primeiro layout.

## Integração com o sistema existente

Foi decidido que, na primeira versão, os dados serão digitados manualmente pelo advogado. Importação de arquivo, leitura do banco ou API ficam para uma etapa posterior, caso tragam benefício e sejam tecnicamente autorizadas.

## Próximos passos

- Inspecionar visualmente o modelo timbrado e preparar uma tela inicial coerente com suas cores.
- Definir as telas do MVP: login, painel, nova minuta, revisão de arquivos e histórico.
- Escolher um primeiro tipo concreto de minuta para protótipo.
- Confirmar a tecnologia principal do site e o banco disponível no servidor local.
- Confirmar formalmente com a UTFPR se o estágio é obrigatório e obter a documentação correspondente.
