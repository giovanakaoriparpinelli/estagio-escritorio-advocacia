# ATA 021 — Backup do banco, revisão de segurança e consolidação

**Data:** 29/10/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Participantes:** Contratante/advogado; estagiário de Engenharia de Software (IA assistida)  
**Referência:** ATA 020  
**Carga horária da semana (26/10 a 29/10, até a data desta ata):** 24 horas

## Contexto

Com o banco concentrando minutas, clientes e prazos, a perda do arquivo seria o principal risco operacional (ATA 016). A semana também reservou tempo para revisar o código de forma geral antes da etapa de homologação com o contratante.

## Decisões

1. **Backup consistente** com a API de backup online do SQLite (seguro mesmo com o serviço em uso), seguido de verificação `PRAGMA integrity_check`. Se a cópia estiver corrompida, ela é descartada e o erro é informado.
2. **Rotação:** mantêm-se as 14 cópias mais recentes.
3. Backups e banco ficam em `data/`, fora do Git. **Cópia para outro disco ou nuvem depende de decisão do contratante**, por envolver dados sujeitos à LGPD.
4. **Revisão de segurança** do código, com os itens abaixo conferidos e cobertos por teste quando possível.

## Revisão de segurança — resultado

| Item | Situação |
|---|---|
| Senhas com hash e sal; nenhuma senha no código | Atendido |
| Token de sessão guardado só como hash | Atendido |
| Consultas SQL parametrizadas (sem concatenação) | Atendido |
| Validação de entrada no servidor, com limites de tamanho | Atendido |
| Permissões por perfil verificadas no servidor (não só na tela) | Atendido |
| Logs e auditoria sem dados pessoais ou texto de minuta | Atendido |
| Texto da API inserido na tela como texto (anti-XSS) | Atendido |
| Acesso restrito a `127.0.0.1` | Atendido |
| HTTPS | **Pendente** (obrigatório antes de uso em rede) |
| Backup fora do computador | **Pendente** (decisão do contratante) |
| Política de retenção e exclusão de dados (LGPD) | **Pendente** (análise jurídica do contratante) |

## Entrega realizada

- `scripts/backup_banco.py`, `tests/test_backup.py`.
- Correção durante a revisão: as conexões do backup não eram fechadas explicitamente, o que travava o arquivo no Windows; passaram a usar `contextlib.closing`.
- Atualização de `README.md` e dos documentos técnicos (modelo de dados, atores, cronograma, registro de horas e diário).

## Validação técnica

Total acumulado: **38 testes automatizados aprovados** (`python -m unittest discover -s tests -t .`).

```powershell
python scripts\backup_banco.py --db data\escritorio.db --destino data\backups
```

## Balanço das semanas 8 a 13

| Semana | ATA | Entrega |
|---|---|---|
| 8 | 016 | Banco SQLite e migrações |
| 9 | 017 | Autenticação, perfis e auditoria |
| 10 | 018 | Revisão, aprovação e versionamento |
| 11 | 019 | API integrada, login e testes ponta a ponta |
| 12 | 020 | Cadastros e painel de prazos |
| 13 | 021 | Backup e revisão de segurança |

## Riscos em aberto

- Uso de dados reais continua **proibido** até haver HTTPS, backup externo e a análise de LGPD do contratante.
- Conversão para PDF ainda sem ferramenta definida (ATA 018).

## Próximo passo

Demonstração ao contratante com dados fictícios, coleta de ajustes e elaboração do relatório parcial do estágio.
