# Requisitos iniciais — Minutas assistidas

## Escopo confirmado

O sistema deverá permitir que um advogado encontre ou informe o nome do cliente e/ou o número do processo, selecione um tipo de minuta para cumprimento de prazo e produza um rascunho revisável.

### Fluxo principal

1. Advogado acessa a área autenticada.
2. Informa cliente e/ou número do processo.
3. Seleciona o tipo de minuta.
4. Sistema coleta os campos necessários e gera um arquivo `.md`.
5. Automação Python converte o Markdown em DOCX usando o modelo `modelo timbrado.docx`.
6. Advogado lê e revisa o DOCX gerado.
7. Após aprovação expressa do advogado, o sistema converte o documento aprovado para PDF.
8. O PDF fica disponível para protocolo/arquivamento conforme o fluxo definido pelo advogado.

## Requisitos de controle

- Cada minuta deve possuir status, por exemplo: `rascunho`, `DOCX gerado`, `em revisão`, `aprovada`, `PDF gerado`.
- O sistema deve preservar o Markdown original, o DOCX gerado e o PDF final.
- A aprovação deve identificar o advogado, data e hora.
- O sistema não deve protocolar automaticamente sem requisito e autorização específicos.
- A geração por IA, se usada, deve ser claramente identificada como assistência; o texto não é parecer nem decisão jurídica automática.

## Usuários e infraestrutura

- Usuários iniciais: Mauro Junior Parpinelli e Patricia Karin Gasparotto.
- Área de login obrigatória.
- Hospedagem local em `C:\\inetpub\\wwwroot`.
- Tecnologias existentes a verificar durante a implementação: PHP, SQL e Python.

## Modelo timbrado

O arquivo `modelo timbrado.docx` foi localizado na raiz do projeto. A inspeção estrutural indica que o timbre está associado ao cabeçalho e a uma imagem incorporada; a conversão deverá preservar esse cabeçalho. A aparência final deverá ser validada pelo contratante com um documento de teste.

## Pendência de integração com o sistema de prazos

Quando perguntei como o sistema atual de prazos poderá fornecer dados, a pergunta ficou sem resposta. Em termos simples: o novo sistema deverá buscar automaticamente dados no sistema antigo ou o advogado digitará/importará esses dados manualmente? As opções são:

- **Manual:** o advogado informa cliente, processo e demais campos.
- **Arquivo:** o sistema antigo exporta CSV, JSON, Excel ou outro arquivo.
- **Banco:** o novo sistema lê uma tabela do banco existente, com autorização e segurança.
- **API:** o sistema antigo oferece uma interface para consulta.

Para o primeiro layout, podemos deixar a integração fora do escopo e usar dados fictícios.
