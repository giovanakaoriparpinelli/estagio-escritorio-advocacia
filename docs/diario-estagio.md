# Diário do estágio

Use uma entrada por sessão de trabalho.

## Modelo

**Data:** AAAA-MM-DD  
**Objetivo:**  
**Atividades realizadas:**  
**Decisões e justificativas:**  
**Evidências/arquivos:**  
**Impedimentos e riscos:**  
**Validação necessária do contratante:**  
**Próximo passo:**

---

# Registro semanal
## Semana de 2026-08-03 a 2026-08-07

**Horas:** 30  
**Atividades realizadas:** Reunião inicial com o contratante; definição do primeiro incremento; registro das respostas e dos requisitos da automação de minutas.  
**Decisões e justificativas:** Escopo limitado ao layout e à minuta de manifestação; usar apenas dados fictícios.  
**Evidências/arquivos:** ATA 001, ATA 002  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Receber o modelo timbrado e definir o tipo de minuta.

## Semana de 2026-08-10 a 2026-08-14

**Horas:** 30  
**Atividades realizadas:** Adoção do registro contínuo em atas; plano de execução em cinco fases.  
**Decisões e justificativas:** Cada sessão com decisão ou entrega gera ata numerada.  
**Evidências/arquivos:** ATA 003, ATA 004  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Preparar o protótipo visual.

## Semana de 2026-08-17 a 2026-08-21

**Horas:** 30  
**Atividades realizadas:** Definição da manifestação simples como primeira minuta; primeiro protótipo navegável; aprovação visual.  
**Decisões e justificativas:** Campos do formulário aprovados provisoriamente; cores e nome aprovados.  
**Evidências/arquivos:** ATA 005 a 007; `prototype/`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Receber o logotipo.

## Semana de 2026-08-24 a 2026-08-28

**Horas:** 30  
**Atividades realizadas:** Recebimento do logotipo de referência; geração real do Markdown; validação e requisito de uso em celular.  
**Decisões e justificativas:** Site deve funcionar em celular.  
**Evidências/arquivos:** ATA 008 a 010  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Integrar o arquivo do logotipo.

## Semana de 2026-08-31 a 2026-09-04

**Horas:** 30  
**Atividades realizadas:** Logotipo integrado; conversão de Markdown para DOCX com modelo timbrado; geração do DOCX pelo próprio sistema.  
**Decisões e justificativas:** DOCX gerado por botão no site, sem exigir PowerShell.  
**Evidências/arquivos:** ATA 011 a 013; `scripts/md_to_docx.py`; `services/document_service.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Conectar o formulário ao serviço.

## Semana de 2026-09-07 a 2026-09-11 (feriado em 07/09)

**Horas:** 24  
**Atividades realizadas:** Impedimento relatado na geração do DOCX; diagnóstico (formulário ainda não ligado ao endpoint).  
**Decisões e justificativas:** Serviço restrito a 127.0.0.1; sem dados reais.  
**Evidências/arquivos:** ATA 014  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Corrigir o fluxo de interface.

## Semana de 2026-09-14 a 2026-09-18

**Horas:** 30  
**Atividades realizadas:** Botão "Gerar DOCX" integrado; publicação no GitHub; reorganização de pastas; dados do estágio confirmados; documentação técnica (modelo de dados, atores, metodologia, lógica de programação).  
**Decisões e justificativas:** Kanban semanal simplificado como metodologia.  
**Evidências/arquivos:** ATA 015; `docs/`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Persistência em banco.

## Semana de 2026-09-21 a 2026-09-25

**Horas:** 30  
**Atividades realizadas:** Esquema SQLite com migrações; gravação de minutas.  
**Decisões e justificativas:** SQLite; valores em centavos; banco fora do Git.  
**Evidências/arquivos:** ATA 016; `services/database.py`, `services/minutas.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Autenticação e perfis.

## Semana de 2026-09-28 a 2026-10-02

**Horas:** 30  
**Atividades realizadas:** Login, sessões, perfis, bloqueio por tentativas e trilha de auditoria.  
**Decisões e justificativas:** PBKDF2; token guardado só como hash; mensagens genéricas de erro.  
**Evidências/arquivos:** ATA 017; `services/auth.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Fluxo de revisão e aprovação.

## Semana de 2026-10-05 a 2026-10-09

**Horas:** 30  
**Atividades realizadas:** Estados da minuta, aprovação só pelo advogado, versionamento e imutabilidade da aprovada.  
**Decisões e justificativas:** Aprovada é imutável (regra e gatilho no banco); PDF adiado.  
**Evidências/arquivos:** ATA 018  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** API e interface integradas.

## Semana de 2026-10-13 a 2026-10-16 (feriado em 12/10)

**Horas:** 24  
**Atividades realizadas:** API HTTP, interface com login e testes ponta a ponta.  
**Decisões e justificativas:** Protótipo entregue pelo próprio serviço; CSP e limites de entrada.  
**Evidências/arquivos:** ATA 019; `prototype/app.js`; `tests/test_api.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Cadastros e prazos.

## Semana de 2026-10-19 a 2026-10-23

**Horas:** 30  
**Atividades realizadas:** Cadastros de clientes, processos (padrão CNJ) e prazos; painel de próximos 15 dias.  
**Decisões e justificativas:** Sistema não calcula prazos processuais; lançamento manual.  
**Evidências/arquivos:** ATA 020; `services/cadastros.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Backup e revisão de segurança.

## Semana de 2026-10-26 a 2026-10-29

**Horas:** 24  
**Atividades realizadas:** Backup com verificação de integridade; revisão de segurança; consolidação da documentação.  
**Decisões e justificativas:** Backup externo e HTTPS pendentes de decisão.  
**Evidências/arquivos:** ATA 021; `scripts/backup_banco.py`  
**Impedimentos e riscos:** ver a ata correspondente.  
**Validação necessária do contratante:** demonstração ao fim da semana.  
**Próximo passo:** Homologação com o contratante e relatório parcial.
