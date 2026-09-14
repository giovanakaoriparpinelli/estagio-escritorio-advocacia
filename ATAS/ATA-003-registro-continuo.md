# ATA 003 — Registro contínuo do desenvolvimento

**Data:** 14/09/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Participantes:** Contratante/advogado; estagiário de Engenharia de Software (IA assistida)  
**Referências:** ATA 001 e ATA 002

## 1. Decisão registrada

O contratante solicitou que todas as decisões, respostas, alterações de escopo, entregas, impedimentos e próximos passos do estágio sejam documentados continuamente em atas numeradas, sem necessidade de solicitar cada registro.

Essa regra passa a fazer parte do processo permanente do projeto e foi incluída nas instruções do estagiário em `AGENTS.md`.

## 2. Estado atual consolidado

- Produto: plataforma local para gestão jurídica e automação assistida.
- Primeiro caso de uso: minutas simples para cumprimento de prazo processual.
- Usuários iniciais: Mauro Junior Parpinelli e Patricia Karin Gasparotto.
- Dados iniciais: cliente, número do processo e informações necessárias à minuta.
- Entrada inicial: digitação manual pelo advogado.
- Fluxo: Markdown → DOCX com modelo timbrado → revisão → aprovação → PDF.
- Hospedagem: local, em `C:\\inetpub\\wwwroot`.
- Tecnologias existentes a verificar: PHP, SQL e Python.
- Primeira entrega: layout do site baseado em `modelo timbrado.docx`.
- Integração com o sistema de prazos: posterior ao MVP inicial.

## 3. Processo de documentação adotado

O estagiário deverá criar uma nova ata quando houver impacto no projeto. Cada ata deverá conter, quando aplicável:

- data e participantes;
- objetivo ou contexto;
- informações fornecidas pelo contratante;
- decisões tomadas;
- requisitos e alterações de escopo;
- perguntas pendentes;
- tarefas e responsáveis;
- riscos e validações necessárias;
- referência aos arquivos produzidos.

## 4. Próximos passos

1. Preparar o primeiro protótipo visual do layout.
2. Validar cores, identidade e estrutura com o modelo timbrado.
3. Definir o primeiro tipo específico de minuta.
4. Confirmar as tecnologias e o banco existentes no servidor local.
5. Manter o registro contínuo em `ATAS/` durante todo o desenvolvimento.

## 5. Observação

As atas são registros de acompanhamento do projeto e do estágio. Elas não substituem documentos oficiais da UTFPR, contratos, termos de compromisso, políticas internas ou documentos jurídicos.
