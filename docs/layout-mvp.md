# Layout inicial do MVP

## Telas

- **Login:** identificação do escritório, usuário, senha e acesso restrito aos dois advogados.
- **Painel:** botão “Criar nova minuta”, resumo por status e atividades recentes.
- **Nova minuta:** cliente, número do processo, tipo de minuta e campos específicos.
- **Revisão e histórico:** Markdown, DOCX, status, aprovação expressa, PDF e versões.

## Fluxo visual

`Rascunho` → `Markdown gerado` → `DOCX gerado` → `Em revisão` → `Aprovada` → `PDF gerado`.

Uma minuta aprovada não deve ser sobrescrita silenciosamente; alterações posteriores criam nova versão.

## Identidade e aceite

O layout usará o arquivo `modelo timbrado.docx` como referência. O contratante validará cores, logotipo, tipografia e espaçamentos na primeira tela navegável.

O layout será aceito quando permitir navegar pelo protótipo, criar uma minuta, compreender seus status e reconhecer a identidade visual do modelo.
