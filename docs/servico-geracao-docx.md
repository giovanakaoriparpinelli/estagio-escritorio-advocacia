# Serviço local de geração de DOCX

O arquivo `services/document_service.py` expõe o endpoint local `POST /api/minutas/docx`. Ele recebe JSON com `cliente`, `processo`, `finalidade`, `fatos` e `pedido`, usa o modelo timbrado e devolve um DOCX para download.

## Executar

Na raiz do projeto:

```powershell
python services\document_service.py
```

O serviço escuta somente em `127.0.0.1:8765` nesta fase de desenvolvimento.

## Observações

- Não há autenticação neste protótipo.
- Não usar dados reais ainda.
- O serviço não gera PDF e não implementa aprovação.
- Antes de produção, devem ser adicionados autenticação, autorização, logs sem dados sensíveis, limites de tamanho, armazenamento seguro e integração controlada com o IIS.
