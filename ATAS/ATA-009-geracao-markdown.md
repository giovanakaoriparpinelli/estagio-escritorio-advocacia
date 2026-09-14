# ATA 009 — Geração real do Markdown

**Data:** 03/08/2026  
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

## Anexo técnico — lógica de programação (detalhado posteriormente)

Trecho de `prototype/index.html` responsável pela geração descrita acima, com a explicação completa em [`docs/logica-de-programacao.md`](../docs/logica-de-programacao.md):

```js
function values(){
  const d=new FormData(form);
  return {
    cliente:String(d.get('cliente')||'').trim(),
    processo:String(d.get('processo')||'').trim(),
    finalidade:String(d.get('finalidade')||'').trim(),
    fatos:String(d.get('fatos')||'').trim(),
    pedido:String(d.get('pedido')||'').trim()
  };
}
function makeMarkdown(v){
  return `# Manifestação simples\n\n**Cliente/parte representada:** ${v.cliente}  \n**Processo:** ${v.processo}\n\n## Finalidade\n\n${v.finalidade}\n\n## Fatos e informações\n\n${v.fatos}\n\n## Pedido ou providência\n\n${v.pedido}\n`;
}
function valid(v){ return Object.values(v).every(Boolean); }
```

`values()` lê o formulário com `FormData` e devolve um objeto simples; `valid()` confirma que nenhum campo obrigatório ficou vazio antes de permitir o download; `makeMarkdown()` monta o texto final usando *template literals* do JavaScript, no formato Markdown descrito no item "Funcionamento" acima.
