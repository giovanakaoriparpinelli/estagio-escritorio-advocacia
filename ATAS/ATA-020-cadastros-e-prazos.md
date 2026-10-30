# ATA 020 — Cadastros de clientes, processos e prazos

**Data:** 23/10/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Participantes:** Contratante/advogado; estagiário de Engenharia de Software (IA assistida)  
**Referência:** ATA 019 e `docs/modelo-de-dados.md`  
**Carga horária da semana (19/10 a 23/10):** 30 horas

## Contexto

Até aqui, clientes e processos só nasciam como efeito colateral da criação de uma minuta. Para o sistema servir ao controle do escritório, eles precisam ser cadastrados de forma explícita, e os prazos devem aparecer com destaque. Conforme a ATA 001, a **integração com o sistema de prazos já existente continua fora do escopo**: os prazos aqui são lançados manualmente, apenas para apoiar as minutas.

## Decisões

1. **Número de processo no padrão CNJ** (`0000000-00.0000.0.00.0000`), validado no cadastro; duplicidade recusada.
2. **CPF/CNPJ** opcional, aceito apenas em formato plausível. Não há validação de dígitos verificadores nesta etapa.
3. **Prazos** com data ISO validada (31/02 é recusado), descrição e vínculo obrigatório com um processo; marcação de "cumprido".
4. **Painel de prazos:** lista dos não cumpridos nos próximos 15 dias, **incluindo os já vencidos**, ordenados do mais urgente ao menos; vencidos aparecem em vermelho.
5. A auditoria registra criação de cliente, processo e prazo e o cumprimento do prazo, sem gravar nome ou descrição.
6. O sistema **não calcula prazos processuais** nem conta dias úteis: a data é informada pelo advogado. Essa decisão evita erro jurídico atribuído ao software.

## Entrega realizada

- `services/cadastros.py` e rotas `/api/clientes`, `/api/processos`, `/api/prazos`, `/api/prazos/{id}/cumprido` e `/api/painel`.
- Painel "Próximos 15 dias" na interface.
- `tests/test_cadastros.py`.

## Validação técnica

Total acumulado: 36 testes aprovados. Os 5 novos cobrem: número fora do padrão, cliente inexistente, processo duplicado, CPF/CNPJ inválido, ordenação e inclusão de prazos vencidos, prazo cumprido saindo da lista, data inválida e acesso negado ao perfil `cliente`.

## Anexo técnico — trecho comentado

```python
def prazos_proximos(conexao, usuario, dias=15, hoje=None):
    limite = (hoje + timedelta(days=dias)).isoformat()
    # não cumpridos até o limite; vencidos entram porque a data é menor que o limite
    linhas = conexao.execute("... WHERE z.cumprido = 0 AND z.data <= ? ORDER BY z.data, z.id", (limite,))
    for linha in linhas:
        item["dias_restantes"] = (date.fromisoformat(item["data"]) - hoje).days
        item["vencido"] = item["dias_restantes"] < 0
```

O parâmetro `hoje` existe para tornar o teste determinístico (data fixa em vez do relógio do computador).

## Limitações e riscos

- Sem edição ou exclusão de clientes e processos nesta etapa (evita perda acidental de dados).
- Risco jurídico: prazo lançado errado gera falsa segurança. Orientação: o painel é apoio, não substitui a agenda oficial do escritório.

## Pendências para o contratante

- Informar quais outros dados do processo são essenciais (por exemplo, vara, comarca, partes contrárias).
- Decidir se, em etapa futura, os prazos serão importados do sistema atual.

## Próximo passo

Rotina de backup do banco e revisão de segurança do conjunto.
