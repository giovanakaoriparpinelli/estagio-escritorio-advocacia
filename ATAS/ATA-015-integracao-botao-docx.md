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

## Controle de versão e publicação no GitHub

O projeto foi inicializado como repositório Git (`git init`) e publicado no GitHub, em repositório público: `https://github.com/giovanakaoriparpinelli/estagio-escritorio-advocacia`. Foi criado um `.gitignore` para excluir arquivos gerados automaticamente (como `__pycache__`), e o histórico de commits passou a documentar cada etapa do trabalho de forma incremental.

## Reorganização da estrutura do projeto

Os relatórios de estágio foram movidos para uma pasta dedicada `relatorios/`, e os arquivos de identidade visual (`LOGO.png` e `modelo timbrado.docx`) para `identidade-visual/`. As referências a esses arquivos foram atualizadas em `services/document_service.py` e `scripts/md_to_docx.py`, e a seção "Estrutura" do `README.md` foi revisada para refletir a organização atual das pastas.

## Confirmação dos dados do estágio

Foram confirmados e registrados em `docs/dados-do-estagio.md`: modalidade (obrigatório, sem remuneração), carga horária (6 horas diárias, das 09h00 às 11h00 e das 13h00 às 17h00, de segunda a sexta-feira), período (03/08/2026 a 03/12/2026), supervisor (Mauro, advogado) e professora orientadora (Gisele Santana). A análise da carga horária indica um total líquido estimado de 510 horas no período, uma folga de 150 horas acima do mínimo de 360 horas exigido para o estágio obrigatório.

## Documentação técnica ampliada

Foram criados os documentos `docs/modelo-de-dados.md` (modelo de entidades e relacionamentos proposto), `docs/atores-e-usuarios.md` (perfis de usuário do sistema), `docs/metodologia-agil.md` (metodologia ágil simplificada — Kanban semanal — e cronograma do projeto) e `docs/logica-de-programacao.md` (explicação, com trechos de código reais, do fluxo de geração de minutas em DOCX), com diagramas correspondentes em `docs/diagramas/`. Esse conteúdo também foi incorporado como anexos técnicos às atas 001, 004, 009, 012 e 013, e consolidado em uma nova versão do relatório de estágio (`relatorios/Relatorio_Estagio_Giovana_v4.docx`).

## Próximo passo

Implementar a etapa de revisão/aprovação e a conversão do DOCX aprovado para PDF.
