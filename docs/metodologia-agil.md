# Metodologia ágil e cronograma

## Por que uma metodologia simplificada

A equipe do projeto tem duas pessoas: o advogado supervisor (Mauro), que também atua como responsável pelo produto e revisor final, e a estagiária (Giovana), única desenvolvedora. Frameworks ágeis completos (Scrum com múltiplos papéis, cerimônias diárias, sprints fixos de 2 semanas) foram desenhados para times maiores e adicionariam processo sem agregar valor aqui. Por isso o projeto adota um **Kanban semanal simplificado**, inspirado no Scrumban, mantendo só o que é útil numa equipe pequena: visibilidade do que está em andamento e um ritmo fixo de revisão.

## Quadro de trabalho

| Coluna | Significado |
|---|---|
| **Backlog** | Ideias e pendências ainda não iniciadas (ex.: itens listados em "Próximos passos" das atas e do README). |
| **Em andamento** | O que a estagiária está desenvolvendo na semana corrente. |
| **Em revisão** | Entregue e aguardando validação do advogado supervisor. |
| **Concluído** | Aprovado e registrado em ata. |

Sugestão de ferramenta: como o projeto já está no GitHub, o próprio **GitHub Projects** (quadro Kanban integrado a Issues) pode hospedar esse board sem precisar de outra ferramenta — mas um quadro simples em texto/markdown também atende, dado o tamanho da equipe.

## Ritmo semanal

- **Toda segunda-feira** (ou terça-feira, quando a segunda é feriado): definição do foco da semana. **Ao fim da semana** (normalmente na sexta-feira): demonstração ao contratante e registro em uma nova ata (ver [`ATAS/`](../ATAS/)). Esse é o ritmo observado nas atas do projeto — ao menos uma por semana.
- **Revisão contínua**: como o advogado supervisor participa das sessões, a revisão de cada entrega acontece no mesmo dia em que é apresentada, sem esperar o fim de um ciclo maior (diferente de uma sprint review tradicional).
- **Sem estimativas formais** (story points, velocity): dado o volume de trabalho e o tamanho da equipe, cada item do backlog é tratado como uma entrega única a ser concluída na semana.

## Cronograma (fases × tempo)

O cronograma une o [plano de atividades](plano-de-atividades.md) (fases de trabalho) ao [período oficial do estágio](dados-do-estagio.md) (03/08/2026 a 03/12/2026). As atas 001 a 021 registram as semanas 1 a 13 do estágio (03/08 a 29/10/2026); as horas de cada semana constam em [`registro-de-horas.md`](registro-de-horas.md).

```mermaid
gantt
    dateFormat YYYY-MM-DD
    title Cronograma do projeto (estágio de 03/08 a 03/12/2026)
    axisFormat %d/%m

    section Executado
    Descoberta e requisitos (ATA 001-004) :done, t0, 2026-08-03, 2026-08-14
    Protótipo navegável e identidade visual (ATA 005-008) :done, t1, 2026-08-17, 2026-08-28
    Geração de Markdown e DOCX (ATA 009-013) :done, t2, 2026-08-26, 2026-09-04
    Botão DOCX e documentação técnica (ATA 014-015) :done, t3, 2026-09-08, 2026-09-18
    Banco de dados SQLite (ATA 016) :done, t4, 2026-09-21, 2026-09-25
    Autenticação perfis e auditoria (ATA 017) :done, t5, 2026-09-28, 2026-10-02
    Revisão e aprovação das minutas (ATA 018) :done, t6, 2026-10-05, 2026-10-09
    API integrada login e testes (ATA 019) :done, t7, 2026-10-13, 2026-10-16
    Cadastros e prazos (ATA 020) :done, t8, 2026-10-19, 2026-10-23
    Backup e revisão de segurança (ATA 021) :done, t9, 2026-10-26, 2026-10-29

    section Planejado
    Homologação com o contratante e ajustes :t10, 2026-11-03, 2026-11-19
    Documentação e relatório final :t11, 2026-11-23, 2026-12-03
```

![Cronograma do projeto](diagramas/cronograma.png)

> As barras de "Executado" refletem as atas 001 a 021 (semanas 1 a 13); as de "Planejado" são previsões, ajustadas a cada ciclo semanal conforme o progresso real e registradas em ata.

## Critérios de "pronto" (Definition of Done)

Um item só passa para "Concluído" quando:

1. o código/funcionalidade foi testado manualmente pela estagiária;
2. o resultado foi demonstrado e aprovado pelo advogado supervisor;
3. o código foi commitado e enviado ao GitHub (`git push`);
4. a decisão/entrega foi registrada na ata da semana.
