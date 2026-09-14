# ATA 015 — Integração do botão de geração DOCX

**Data:** 14/09/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 014

## Entrega realizada

O formulário do protótipo foi conectado ao serviço Python local. Agora há um botão “Gerar DOCX” que envia os dados preenchidos ao endpoint e inicia o download do documento retornado.

Também foram adicionados:

- suporte CORS para o protótipo local;
- mensagens de carregamento, sucesso e erro;
- botão para baixar Markdown;
- logotipo no cabeçalho do protótipo;
- adaptação visual para celular.

## Teste técnico

O serviço foi iniciado em `127.0.0.1:8765` e testado com dados fictícios. A requisição retornou um DOCX válido com aproximadamente 312 KB.

## Como testar

Terminal 1:

```powershell
cd F:\ESTAGIO_GIOVANA
python services\document_service.py
```

Depois, abrir `prototype/index.html`, preencher os campos fictícios e clicar em “Gerar DOCX”.

## Limitações

- O serviço precisa ser iniciado manualmente nesta fase.
- Ainda não há autenticação, persistência, aprovação ou geração de PDF.
- O uso de dados reais continua proibido no protótipo.

## Próximo passo

Implementar a etapa de revisão/aprovação e a conversão do DOCX aprovado para PDF.
