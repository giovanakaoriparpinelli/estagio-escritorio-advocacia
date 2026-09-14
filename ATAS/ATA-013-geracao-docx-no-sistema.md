# ATA 013 — Geração de DOCX pelo próprio sistema

**Data:** 31/08/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Referência:** ATA 012

## Decisão do contratante

Foi confirmado que o usuário não deve executar comandos no PowerShell para gerar documentos. A geração do DOCX deverá ocorrer por botão dentro do site.

## Entrega inicial

Foi criado um serviço local em `services/document_service.py`, usando a biblioteca padrão HTTP do Python. O endpoint `POST /api/minutas/docx` recebe os dados da manifestação, chama o conversor existente e devolve o arquivo DOCX.

## Limitações atuais

- O endpoint ainda não está conectado ao formulário HTML.
- Não há autenticação, aprovação, persistência ou PDF.
- O serviço escuta apenas em `127.0.0.1` para desenvolvimento.
- Dados reais não devem ser utilizados.

## Próximo passo

Conectar o botão do protótipo ao endpoint local e criar a etapa explícita de revisão/aprovação antes da conversão para PDF.
