# ATA 018 — Fluxo de revisão e aprovação das minutas

**Data:** 09/10/2026  
**Projeto:** Plataforma local de gestão jurídica e automação assistida  
**Participantes:** Contratante/advogado; estagiário de Engenharia de Software (IA assistida)  
**Referência:** ATA 017 e ATA 002 (fluxo aprovado)  
**Carga horária da semana (05/10 a 09/10):** 30 horas

## Contexto

O fluxo definido na ATA 002 prevê "leitura e revisão do advogado → aprovação". As regras 8 do `AGENTS.md` e da ATA 001 reforçam que todo texto é rascunho até a revisão do advogado. Esta semana transforma essa regra em comportamento do sistema.

## Decisões

1. **Estados da minuta:** `rascunho` → `em_revisao` → `aprovada` ou `devolvida`.
2. **Somente o perfil `advogado` aprova ou devolve.** A devolução exige motivo escrito.
3. **Aprovada é imutável**, na regra de negócio e também no banco (gatilho `documento_aprovado_imutavel`), de modo que nem uma alteração direta por SQL adultera o texto aprovado.
4. **Correções geram nova versão:** a partir de uma minuta devolvida ou aprovada cria-se um novo rascunho (versão 2, 3…), ligado ao original por `origem_id`. O histórico nunca é sobrescrito.
5. **Exportação marcada:** todo DOCX/Markdown de minuta não aprovada sai com o aviso "RASCUNHO — não aprovado pelo advogado. Revisão obrigatória."; a minuta aprovada traz o nome do revisor e a data da aprovação (UTC).
6. Cada transição de estado é gravada na auditoria (sem o texto da minuta).
7. **Decisão adiada:** a conversão do DOCX aprovado em PDF depende de uma ferramenta de conversão (Word ou LibreOffice) ainda não confirmada no servidor do escritório; fica para a próxima rodada de requisitos.

## Entrega realizada

- Esquema v3 (`status`, `revisado_por`, `revisado_em`, `motivo_devolucao` e o gatilho de imutabilidade).
- Funções `enviar_para_revisao`, `aprovar`, `devolver`, `nova_versao` e `markdown_para_exportacao` em `services/minutas.py`.
- Testes de fluxo completo, permissões, devolução, imutabilidade e exportação.

## Validação técnica

Total acumulado: 25 testes aprovados. Casos cobertos: aprovar sem passar pela revisão (recusado), estagiária tentando aprovar (recusado), devolução sem motivo (recusada), edição de minuta aprovada (recusada), `UPDATE` direto no banco (barrado pelo gatilho), versão 2 criada a partir da devolvida, e auditoria que não contém o texto das minutas.

## Anexo técnico — trecho comentado

```python
def aprovar(conexao, usuario, minuta_id):
    exigir_perfil(usuario, "advogado")                 # 1) quem pode
    return _mudar_status(conexao, usuario, minuta_id,
                         ("em_revisao",), "aprovada",   # 2) de qual estado para qual
                         "minuta_aprovada", revisao=True)   # 3) registra revisor, data e auditoria
```

## Limitações e riscos

- Um advogado pode aprovar uma minuta criada por ele mesmo; se o escritório quiser dupla conferência, a regra pode ser endurecida.
- A aprovação é do texto como armazenado; o sistema não verifica o conteúdo jurídico (responsabilidade exclusiva do advogado).

## Pendências para o contratante

- Validar os rótulos dos estados e o aviso de rascunho que sai nos documentos.
- Informar qual ferramenta de conversão para PDF está disponível no servidor.

## Próximo passo

Expor o fluxo por uma API HTTP, integrar a interface do protótipo (login, lista e ações) e criar testes de ponta a ponta.
