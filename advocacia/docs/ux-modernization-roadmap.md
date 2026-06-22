# Modernização UX - App Advocacia

Documento permanente de acompanhamento do projeto de modernização de experiência do usuário.

**Criado:** 2026-06-09
**Última atualização:** 2026-06-09 (Etapa 03 — labels verdes do glossário)
**App:** `advocacia` (Frappe v16)

---

## Objetivos

* Simplificar a experiência do usuário
* Aplicar o Glossário Oficial Sprint 1A
* Reduzir complexidade percebida
* Melhorar navegação
* Preservar compatibilidade total com o banco de dados

---

## Restrições

Nunca:

* Renomear DocTypes EN
* Renomear Roles
* Renomear Slugs de Relatórios
* Renomear Rotas
* Renomear Placeholders Word
* Alterar Schema
* Alterar Child Tables
* Alterar Dados de Produção

---

## Glossário Oficial Sprint 1A

### Princípios

1. **Singular** = registro / formulário. **Plural** = lista, menu, seção.
2. **Honorários** = contrato de prestação de serviços advocatícios (`Fee Agreement`). **Recebimentos** = parcelas a receber do cliente (`Legal Payment`). **Custas** = despesas processuais (`Court Cost`). **Despesas** = gastos do escritório (`Office Expense`). Termos distintos, não intercambiáveis.
3. **Cobrança de Serviço** (`Service Record` + `Legal Act Item`) = faturamento por atos avulsos, separado de honorários contratuais.
4. Nome interno Frappe (coluna "Nome técnico") **permanece inalterado**.
5. **Recebimento** = dinheiro que ENTRA (do cliente pro escritório). **Pagamento / Despesa** = dinheiro que SAI (do escritório pra fora). Nunca misturar. Nunca usar "Pagamento" para entrada.

### O Modelo Financeiro do Escritório

O escritório tem **duas fontes de receita** e **duas categorias de despesa**.

**RECEITAS (dinheiro que entra):**

Caminho 1 — Honorários contratuais:
Fee Agreement → Gerar Parcelas → Legal Payment (parcelas a receber)

Caminho 2 — Serviços avulsos:
Service Record + Legal Act Item → Sincronizar Cobrança → Legal Payment (cobrança avulsa)

Ambos geram Legal Payment, mas com origens distintas.

**DESPESAS (dinheiro que sai):**

Custas Processuais (Court Cost) — despesa judicial vinculada a processo. Quem arca: Escritório ou Cliente (reembolso).

Despesas do Escritório (Office Expense) — gasto operacional sem vínculo a processo.

### 1. App, módulo e painel

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Aplicativo | `advocacia` | Advocacia |
| Módulo / workspace | `Advocacia` | Advocacia |
| Painel principal | (rota atual) | Painel do Escritório |
| Atalho no menu | — | Painel |

### 2. Seções do menu lateral

| Conceito | Nome oficial |
|----------|--------------|
| Seção operacional diária | Dia a Dia |
| Seção hub do caso/processo | Gestão de Casos |
| Seção financeira | Financeiro |
| Seção analytics | Relatórios |
| Seção cadastros mestre | Cadastros |
| Seção admin | Administração |

### 3. DocTypes — transacionais e operacionais

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Caso / processo (hub) | `Legal Case` | Processo | Processos |
| Cliente | `Client` | Cliente | Clientes |
| Contrato de honorários | `Fee Agreement` | Contrato de Honorários | Contratos de Honorários |
| Parcela a receber do cliente | `Legal Payment` | Recebimento | Recebimentos |
| Audiência | `Hearing` | Audiência | Audiências |
| Prazo processual | `Deadline` | Prazo | Prazos |
| Tarefa interna | `Legal Task` | Tarefa | Tarefas |
| Custa processual | `Court Cost` | Custa Processual | Custas Processuais |
| Cobrança de atos avulsos | `Service Record` | Cobrança de Serviço | Cobranças de Serviço |
| Comunicação com cliente | `Case Communication` | Comunicação | Comunicações |
| Registro de horas | `Time Entry` | Registro de Horas | Registro de Horas |
| Documento do processo | `Case Document` | Documento do Processo | Documentos do Processo |
| Despesa do escritório | `Office Expense` | Despesa do Escritório | Despesas do Escritório |
| Configuração single | `Office Settings` | Configurações do Escritório | Configurações do Escritório |

### 4. DocTypes — cadastros auxiliares

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Comarca | `Jurisdiction` | Comarca | Comarcas |
| Tribunal | `Court` | Tribunal | Tribunais |
| Vara | `Court Branch` | Vara | Varas |
| Fase processual | `Case Phase` | Fase Processual | Fases Processuais |
| Modelo Word | `Document Template` | Modelo de Documento | Modelos de Documento |
| Kit de documentos | `Document Kit` | Kit de Documentos | Kits de Documentos |
| Categoria de documento | `Document Category` | Categoria de Documento | Categorias de Documento |

### 5. Child tables

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Parcela do contrato | `Fee Installment` | Parcela do Contrato |
| Ato cobrado | `Legal Act Item` | Ato Cobrado |
| Item do kit | `Document Kit Item` | Item do Kit |

### 6. Relatórios

| Slug (intocável) | Nome exibido atual | Nome oficial Sprint 1A | `ref_doctype` | Onde aparece |
|------------------|-------------------|------------------------|---------------|--------------|
| `produtividade` | Produtividade | Produtividade | `Legal Case` | sidebar, workspace |
| `horas_por_servico` | Horas por Serviço | Horas por Processo | `Time Entry` | sidebar, workspace |
| `inadimplencia` | Inadimplência | Inadimplência | `Legal Payment` | sidebar, workspace, painel |
| `fluxo_de_caixa` | Fluxo de Caixa / Fluxo de Caixa Projetado | Fluxo de Caixa Projetado | `Legal Payment` | sidebar, workspace |
| `honorarios_por_cliente` | Honorários por Cliente | Honorários por Cliente | `Fee Agreement` | sidebar, workspace |
| `carteira_ativa` | Carteira Ativa | Carteira Ativa | `Legal Case` | sidebar, workspace |

**Nota:** slugs permanecem inalterados (restrição VM). Apenas labels de menu/workspace/report title são elegíveis para correção.

### 7. Abas e painéis dentro do Processo (hub)

| Conceito | Nome oficial |
|----------|--------------|
| Dados do processo | Detalhes |
| Audiências vinculadas | Audiências |
| Prazos processuais | Prazos |
| Tarefas internas | Tarefas |
| Área financeira | Financeiro |
| Parcelas de honorários | Recebimentos de Honorários |
| Cobranças de atos avulsos | Serviços Avulsos |
| Custas do processo | Custas Processuais |
| Comunicações | Comunicações |
| Horas | Horas Trabalhadas |
| Documentos | Documentos do Processo |
| Andamento / fases | Fases do Processo |

### 8. Conceitos de domínio (não são DocTypes)

| Conceito | Nome oficial | Definição | Não confundir com |
|----------|--------------|-----------|-------------------|
| Dinheiro que entra do cliente | Recebimento | Qualquer entrada financeira do cliente | Despesa / Custa |
| Contrato fixo de honorários | Honorários Contratuais | Valor acordado no contrato | Serviço avulso |
| Cobrança por ato individual | Serviço Avulso | Ato cobrado fora do contrato | Honorário contratual |
| Despesa judicial do processo | Custa Processual | Gasto judicial pago pelo escritório | Despesa operacional |
| Gasto do escritório | Despesa do Escritório | Gasto operacional sem processo | Custa processual |
| Quem arca com a custa | Responsável pela Custa | Escritório ou Cliente (reembolso) | — |
| Prazo fatal processual | Prazo | Data limite imposta pelo judiciário | Tarefa |
| Atividade interna do escritório | Tarefa | Ação operacional do escritório | Prazo |

### 9. Campos com vazamento de inglês (mapeamento)

| Campo atual (EN) | DocTypes onde aparece | Nome oficial PT |
|------------------|-----------------------|-----------------|
| `Client` (label) | Legal Case, Hearing, Deadline, Legal Task, Fee Agreement, Legal Payment… | Cliente |
| `Court Branch` (label) | Legal Case, Hearing | Vara |
| `Court` (label) | Legal Case | Tribunal |
| `Case Phase` (label) | Legal Case | Fase Processual |
| `Jurisdiction` (label) | Legal Case | Comarca |
| `Legal Task` (chips/ações) | Painel, Case Communication | Tarefa |
| `Legal Payment` (chips/ações) | Painel | Recebimento |
| `+ Client` (chip painel) | Dashboard | + Cliente |

### 10. Fora do glossário UI (intocáveis neste projeto)

| Elemento | Regra |
|----------|--------|
| DocType `name` EN | Permanece (ex.: `Legal Case`, `Legal Payment`) |
| Slugs de relatório | Permanecem |
| Rota do painel | Permanece |
| Placeholders Word | Permanecem em inglês |
| Roles | Permanecem `Advocacia User` / `Advocacia Manager` |
| Fieldnames EN | Permanecem (renomeação de 114 fieldnames já executada) |

### Textos de ajuda financeiros obrigatórios (implementar nas Etapas 07-09)

**Hub do Processo — aba Financeiro (banner):**
O financeiro do processo tem duas fontes de receita: Honorários Contratuais (valor acordado no Contrato de Honorários, dividido em parcelas geradas automaticamente) e Serviços Avulsos (atos individuais cobrados fora do contrato). Ambos geram Recebimentos para controle. Custas Processuais (taxas, perícias) são despesas do processo, não receita.

**Fee Agreement (intro):**
O Contrato de Honorários define o valor e a forma de cobrança dos serviços advocatícios. Após preencher valores e condições, clique em "Gerar Parcelas" para criar os Recebimentos automaticamente. Modos: Diretos (100% escritório) ou Divisão (advogado/cliente indicado).

**Service Record (intro):**
Registre aqui atos individuais prestados ao cliente cobrados FORA do Contrato de Honorários principal. Exemplos: consulta extra, parecer avulso, diligência não prevista. Após adicionar os atos, clique em "Sincronizar Cobrança" para gerar um Recebimento.

**Legal Payment (intro):**
Este registro representa uma parcela a receber (ou já recebida) do cliente. Origem: gerado automaticamente por Contrato de Honorários ou Cobrança de Serviço, ou criado manualmente para entradas avulsas.

**Court Cost (intro):**
Despesas judiciais vinculadas ao processo: taxas judiciais, custas de perícia, emolumentos, cartório. Indique quem arca (Escritório ou Cliente). Se o cliente reembolsa, registre data e valor do reembolso.

**Tooltips obrigatórios:**
- Botão "Gerar Parcelas": Cria ou atualiza os Recebimentos com base nos valores e datas definidos. Parcelas já recebidas não serão alteradas.
- Botão "Sincronizar Cobrança": Gera (ou atualiza) um Recebimento com o valor total dos atos listados.
- Campo "Sucumbência": Honorários devidos pela parte perdedora. Registre percentual ou valor estimado. Recebimento efetivo depende do resultado do processo.

---

## Registro de Etapas

### Etapa 00 — Criar documentação permanente

**Status:** Concluída
**Data:** 2026-06-09
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Criar documentação permanente do projeto com glossário completo.

**Arquivos analisados:** Nenhum (etapa de documentação)

**Mudanças realizadas:** Criação deste documento.

**Arquivos criados:** `docs/ux-modernization-roadmap.md`

**Impactos identificados:** Nenhum (zero alteração no app)

**Riscos identificados:** Nenhum

**Testes executados:** Nenhum

**Resultado:** Base normativa pronta para Sprint 1A.

**Pendências:** —

**Próximas etapas:** Etapa 04 — auditoria pós-implementação (revisão manual + itens âmbar restantes)

---

### Etapa 03 — Aplicar mudanças verdes do glossário

**Status:** Concluída
**Data:** 2026-06-09
**Branch:** `ux/step-03-green-risk-labels`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Aplicar exclusivamente divergências classificadas como risco **V** (labels, traduções, menu, seções) do Glossário Sprint 1A, sem alterar schema, DocType names, rotas ou placeholders Word.

**Commits (por grupo funcional):**

| Grupo | Commit | Descrição |
|-------|--------|-----------|
| 1 | `3816ee1` | Legal Case: Serviços → Processos (menu, translations, hub, satélites, relatórios) |
| 2 | `5d1792c` | Financeiro: Recebimentos, Contratos de Honorários, Cobranças de Serviço, etc. |
| 3 | `412804e` | Cadastros auxiliares + campos EN (Cliente, Vara, Tribunal, Comarca, Tarefa) |
| 3b | *(HEAD−1)* | Labels restantes: Office Expense, Service Record, Horas Trabalhadas |
| 4 | — | Deduplicação sidebar: **não necessária** (Etapa 01 confirmou 28 links únicos) |

**Arquivos principais:** `setup/translations.py`, `setup/sidebar.py`, `workspace_sidebar/advocacia.json`, `workspace/advocacia/advocacia.json`, `fixtures/workspace.json`, `adv_case_nav.js`, `case_hub.js`, `public/js/painel/*`, 20+ JSON de DocTypes, `add_field_descriptions.py`, relatórios (labels em `.py`/`.js`).

**DIV resolvidas (V + hub/painel tocados):** DIV-001–DIV-009, DIV-011–DIV-035, DIV-036–DIV-038, DIV-040–DIV-046, DIV-047 *(parcial — mapas ainda duplicados, ver DT-01)*.

**DIV pendentes (Etapa 04+):** nenhuma **V** crítica restante no escopo menu/forms; itens **âmbar** de textos de ajuda (DT-06), manual (DT-04), notificações (DT-02).

**Testes:** **311 + 3 = 314** verdes após cada grupo (`bench --site advocacia.local run-tests --app advocacia`).

**Validação:** `migrate` + `bench build --app advocacia` executados; paridade sidebar confirmada via `test_sidebar_json`.

**Pendências Etapa 04:** auditoria visual no browser; unificar `translations.py` ↔ `adv_case_nav.js` (DT-01); textos de ajuda financeiros (DT-06); `generate_manual.py` / manual (DT-04); notificações EN (DT-02).

**Próximas etapas:** Etapa 04 — auditoria de aderência pós-implementação

---

### Etapa 02 — Corrigir drift estrutural sidebar

**Status:** Concluída
**Data:** 2026-06-09
**Branch:** `ux/step-02-sidebar-sync`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Eliminar inconsistências estruturais entre `sidebar.py` e `workspace_sidebar/advocacia.json` (sem alterar labels).

**Diagnóstico (Fase 0):**
- `sidebar.py`: **28 links**, **5 seções**
- `workspace_sidebar/advocacia.json`: **28 links**, **5 seções** — paridade perfeita label/`link_to`/`link_type`
- `workspace/advocacia/advocacia.json` e `fixtures/workspace.json`: **28 links** — `link_to`/`link_type` idênticos; divergência de label apenas em #20 (Fluxo de Caixa vs Fluxo de Caixa Projetado) — **fora do escopo** (label, Etapa posterior)
- Targets órfãos: **nenhum** (todos DocTypes/Reports/Page existem no app)
- Docstring obsoleta em `_validate_sidebar_links`: citava **26 links** (drift documental)

**Mudanças realizadas:**
- Corrigida docstring de `_validate_sidebar_links` (26 → 28 links)
- Criado `tests/test_sidebar_json.py` (paridade links, seções, targets no disco)
- Nenhuma alteração necessária em `workspace_sidebar/advocacia.json` (já sincronizado)

**Arquivos modificados:**
- `advocacia/advocacia/setup/sidebar.py`
- `advocacia/advocacia/tests/test_sidebar_json.py` (novo)
- `docs/ux-modernization-roadmap.md`

**Contagem links:** antes 28 / depois 28 (paridade confirmada; drift era apenas docstring + ausência de teste)

**Testes:** 311 + 3 = **314** verdes (`test_sidebar_json` × 3)

**Resultado:** Guardrail estrutural permanente; sidebar JSON e Python alinhados.

**Pendências:** Etapa 03+ (labels/glossário) — não misturar nesta branch

**Próximas etapas:** Etapa 03 — `translations.py` e labels de campos JSON

---

### Etapa 01 — Auditoria de aderência ao glossário

**Status:** Concluída
**Data:** 2026-06-09
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Mapear todas as ocorrências de termos que divergem do Glossário Sprint 1A (somente leitura).

**Arquivos analisados:**
- `advocacia/advocacia/setup/sidebar.py`
- `advocacia/workspace_sidebar/advocacia.json`
- `advocacia/advocacia/workspace/advocacia/advocacia.json`
- `advocacia/fixtures/workspace.json`
- `advocacia/advocacia/setup/translations.py`
- `advocacia/public/js/adv_case_nav.js`
- `advocacia/public/js/case_hub.js`
- `advocacia/public/js/painel/*.js`
- `advocacia/advocacia/doctype/*/*.json` (26 DocTypes)
- `advocacia/advocacia/report/*/*.json` (6 relatórios)
- `advocacia/fixtures/notification.json`, `print_format.json`, `kanban_board.json`
- `advocacia/hooks.py` (fixtures)

**Mudanças realizadas:** Atualização deste documento (divergências, matriz, relatórios §6, débitos).

**Arquivos criados:** Nenhum (somente edição do roadmap).

**Impactos identificados:** 47 divergências catalogadas (DIV-001–DIV-047); 0 alterações no app.

**Riscos identificados:** Duplicação de mapas de labels (`translations.py` vs `adv_case_nav.js`); notificações e custom fields Event em inglês exposto ao admin.

**Testes executados:** Nenhum (auditoria read-only).

**Resultado:** Inventário completo pronto para Sprint 1A (Etapas 02–09).

**Pendências:** Implementar correções por prioridade (menu → translations → forms → hub → painel → help texts).

**Próximas etapas:** Etapa 02 — `translations.py` + sidebar/workspace alinhados ao glossário

---

## Decisões Arquiteturais

### DEC-F01
**Contexto:** `Legal Payment` era chamado de "Pagamento" na interface, criando ambiguidade com custas (que são pagamentos que SAEM).
**Decisão:** Nome oficial **Recebimento** (entrada do cliente). Nunca "Pagamento" para dinheiro que entra.
**Motivação:** Eliminar confusão "pagamento = entrada ou saída?".
**Impacto:** translations, sidebar, hub, dashboard, forms, mensagens.

### DEC-F02
**Contexto:** Usuário não entende quando usar Fee Agreement vs Service Record.
**Decisão:** Explicar a diferença DENTRO do app com textos de ajuda. Fee Agreement = contrato; Service Record = atos avulsos fora do contrato. Ambos geram Legal Payment mas com origens distintas.
**Motivação:** Reduzir erro de cadastro.
**Impacto:** intros JS, descriptions JSON, empty states, manual.

### DEC-F03
**Contexto:** "Cobrança de serviços" é longo e ambíguo.
**Decisão:** Singular: **Cobrança de Serviço**. Plural: **Cobranças de Serviço**.
**Motivação:** Alinhado ao padrão singular/plural do glossário.
**Impacto:** sidebar, translations, hub panels.

### DEC-F04
**Contexto:** Botão "Sincronizar Cobrança" é jargão de sistema.
**Decisão:** Manter label, adicionar tooltip explicativo.
**Motivação:** Custo baixo, impacto alto na compreensão.
**Impacto:** JS do form (tooltip).

### DEC-F05
**Contexto:** Custa processual vs Despesa do escritório são conceitos distintos.
**Decisão:** Manter DocTypes separados. Custa no hub do Processo. Despesa só no menu geral.
**Motivação:** Alinhado à contabilidade jurídica real.
**Impacto:** Nenhum estrutural.

### DEC-001
**Contexto:** `Legal Case` exibido como "Serviço" / "Serviços" na interface.
**Decisão:** Nome oficial **Processo** (registro) / **Processos** (lista).
**Motivação:** Advogado pensa em "processo" ou "caso", não "serviço".
**Impacto:** translations, sidebar, workspace, hub, dashboard.

---

### DEC-002
**Contexto:** Menu sidebar usa **Honorários** como label do DocType `Fee Agreement`.
**Decisão:** Nome oficial na lista/menu: **Contratos de Honorários**. Atalho coloquial “Honorários” aceitável apenas em botões `+` dentro do hub, não como nome do módulo.
**Motivação:** Diferenciar contrato (Fee Agreement) de conceito genérico “honorários”.
**Impacto:** sidebar, workspace, translations, adv_case_nav.

---

## Divergências Encontradas

Inventário read-only (Etapa 01). **47 itens** agrupados por área. Risco: **V** = label/tradução; **A** = hub/painel/mensagem (requer teste); **VM** = proibido alterar neste projeto.

### Menu, workspace e traduções globais

| ID | Termo atual | Glossário Sprint 1A | Onde aparece | Arquivos | Risco |
|----|-------------|---------------------|--------------|----------|-------|
| DIV-001 | Serviços | Processos | Sidebar, workspace, shortcuts, translations | `sidebar.py`, `workspace_sidebar/advocacia.json`, `workspace/advocacia/advocacia.json`, `fixtures/workspace.json`, `translations.py`, `adv_case_nav.js` | V |
| DIV-002 | Pagamentos | Recebimentos | Sidebar, workspace, shortcuts, translations | Idem + `legal_payment_list.js` (filtros UI) | V |
| DIV-003 | Cobrança de serviços | Cobranças de Serviço | Sidebar, workspace, translations | `sidebar.py`, `translations.py`, `adv_case_nav.js`, `case_hub.js` | V |
| DIV-004 | Despesas | Despesas do Escritório | Sidebar, workspace, translations | `sidebar.py`, `translations.py` (`Office Expense`) | V |
| DIV-005 | Honorários (menu DocType) | Contratos de Honorários | Sidebar, workspace, translations | `sidebar.py`, `translations.py` (`Fee Agreement`) | V |
| DIV-006 | Modelos Word | Modelos de Documento | Sidebar, workspace, translations | `sidebar.py`, `translations.py` | V |
| DIV-007 | Horas por Serviço | Horas por Processo | Sidebar, workspace, report label | `sidebar.py`, `horas_por_servico.json` | V |
| DIV-008 | Escritório | Configurações do Escritório | Sidebar, workspace, translations | `sidebar.py`, `translations.py` (`Office Settings`) | V |
| DIV-009 | Configuração do Escritório | Configurações do Escritório | translations.py | `translations.py` | V |
| DIV-010 | Documentos do Processo | Documentos do Processo | OK — manter | — | — |
| DIV-011 | Fluxo de Caixa (sidebar) vs Fluxo de Caixa Projetado (workspace) | Fluxo de Caixa Projetado (uniformizar) | Sidebar vs workspace shortcut | `sidebar.py`, `workspace/advocacia/advocacia.json` | V |

### DocType translations (seed)

| ID | Termo atual | Glossário Sprint 1A | Onde aparece | Arquivos | Risco |
|----|-------------|---------------------|--------------|----------|-------|
| DIV-012 | Parcelas de Honorários (`Fee Installment`) | Parcela do Contrato | Tradução DocType child | `translations.py` | V |
| DIV-013 | Itens de cobrança (`Legal Act Item`) | Ato Cobrado | Tradução DocType child | `translations.py` | V |

### Campos de formulário — inglês exposto (labels JSON)

| ID | Termo atual | Glossário Sprint 1A | Onde aparece | Arquivos | Risco |
|----|-------------|---------------------|--------------|----------|-------|
| DIV-014 | Client | Cliente | 12+ DocTypes (Link) | `legal_case.json`, `hearing.json`, `deadline.json`, `legal_task.json`, `fee_agreement.json`, `legal_payment.json`, `service_record.json`, `court_cost.json`, `time_entry.json`, `case_communication.json` | V |
| DIV-015 | Court Branch | Vara | Legal Case, Hearing | `legal_case.json`, `hearing.json` | V |
| DIV-016 | Court | Tribunal | Legal Case | `legal_case.json` | V |
| DIV-017 | Case Phase | Fase Processual | Legal Case | `legal_case.json` | V |
| DIV-018 | Jurisdiction | Comarca | Legal Case, Court Branch | `legal_case.json`, `court_branch.json` | V |
| DIV-019 | Nome da Jurisdiction | Nome da Comarca | Jurisdiction | `jurisdiction.json` | V |
| DIV-020 | Nome do Court | Nome do Tribunal | Court | `court.json` | V |
| DIV-021 | Nome da Court Branch | Nome da Vara | Court Branch | `court_branch.json` | V |
| DIV-022 | Descrição da Legal Task | Resumo da tarefa | Legal Task | `legal_task.json` | V |
| DIV-023 | Gerar Legal Task / Legal Task Gerada | Gerar Tarefa / Tarefa gerada | Case Communication | `case_communication.json` | V |
| DIV-024 | Percentual Client / Valor Client / Total Client | Percentual do cliente / Valor do cliente / Total cliente | Fee Agreement, Fee Installment | `fee_agreement.json`, `fee_installment.json` | V |
| DIV-025 | Legal Payment (label child) | Recebimento | Fee Installment | `fee_installment.json` | V |
| DIV-026 | Data de Repasse ao Client | Data de repasse ao cliente | Fee Installment | `fee_installment.json` | V |
| DIV-027 | Data de Legal Payment / Forma de Legal Payment | Data de pagamento / Forma de pagamento | Court Cost, Office Expense | `court_cost.json`, `office_expense.json` | V |
| DIV-028 | Repassar ao Client | Repassar ao cliente | Court Cost | `court_cost.json` | V |
| DIV-029 | Vencimento e Legal Payment (section) | Vencimento e pagamento | Office Expense | `office_expense.json` | V |
| DIV-030 | Pagamento (label child Legal Act Item) | Recebimento | Legal Act Item | `legal_act_item.json` | V |
| DIV-031 | Último pagamento | Último recebimento | Service Record | `service_record.json` | V |
| DIV-032 | Serviço (Link label) | Processo | Todos os satélites com `legal_case` | 10+ JSON de DocTypes | V |
| DIV-033 | Cobrança de serviços (Link Legal Payment) | Cobrança de Serviço | Legal Payment | `legal_payment.json` | V |
| DIV-034 | Honorários (Link Fee Agreement) | Contrato de Honorários | Legal Payment | `legal_payment.json` | V |

### Hub Legal Case — abas e painéis

| ID | Termo atual | Glossário Sprint 1A | Onde aparece | Arquivos | Risco |
|----|-------------|---------------------|--------------|----------|-------|
| DIV-035 | Resumo do Serviço | Resumo do Processo | HTML panel | `legal_case.json` | V |
| DIV-036 | Pagamentos (aba/seção hub) | Recebimentos | Tab/section + case_hub KPIs | `legal_case.json`, `case_hub.js` | A |
| DIV-037 | Parcelas de Honorários (painel hub) | Recebimentos de Honorários | `legal_case.json`, `case_hub.js` | A |
| DIV-038 | Cobrança de serviços (painel hub) | Serviços Avulsos | `legal_case.json`, `case_hub.js` | A |
| DIV-039 | Horas (section) | Horas Trabalhadas | `legal_case.json` | V |
| DIV-040 | Pagamentos pendentes (KPI hub) | Recebimentos pendentes | `case_hub.js` | A |

### Painel / ações rápidas / navegação JS

| ID | Termo atual | Glossário Sprint 1A | Onde aparece | Arquivos | Risco |
|----|-------------|---------------------|--------------|----------|-------|
| DIV-041 | Client (chip ação rápida) | Cliente | Painel hero | `public/js/painel/hero.js` | A |
| DIV-042 | Serviço (chip) | Processo | Painel hero | `public/js/painel/hero.js` | A |
| DIV-043 | Legal Task (chip) | Tarefa | Painel hero, timeline fallback | `hero.js`, `timeline.js` | A |
| DIV-044 | Legal Payment (chip) | Recebimento | Painel hero, financeiro | `hero.js`, `financeiro.js` | A |
| DIV-045 | Voltar ao Serviço | Voltar ao Processo | Botão satélites | `adv_case_nav.js` | A |
| DIV-046 | Legal Task (fallback timeline) | Tarefa | Painel timeline | `timeline.js` | A |
| DIV-047 | Mapa duplicado desatualizado | Espelhar glossário | `DOCTYPE_NAV_LABELS` vs `translations.py` | `adv_case_nav.js` | A |

### Itens auditados — conformes ou VM (sem ação UI)

| Item | Status |
|------|--------|
| Slugs relatórios (`produtividade`, `inadimplencia`, …) | VM — intocável |
| DocType names EN | VM — intocável |
| Rota `painel` | VM — intocável |
| Roles Advocacia User/Manager | VM — intocável |
| Fieldnames EN (`legal_case`, `client`, …) | VM — intocável |
| Print formats “Serviço / Processo” no recibo | Aceitável (texto misto explicativo) |
| Botões Gerar Parcelas / Sincronizar Cobrança | Label OK — falta tooltip (DEC-F04, Etapas 07–09) |
| Seções Dia a Dia, Gestão de Casos, Financeiro, Relatórios, Cadastros | Conformes |
| Painel do Escritório (page title) | Conforme |
| Prazos, Audiências, Tarefas, Comunicações (menu) | Conformes |
| Comarca, Vara, Tribunal, Fase Processual (menu) | Conformes |

---

## Matriz de impacto (Etapa 01)

| Área | Divergências | Arquivos estimados | Etapa alvo sugerida | Risco dominante |
|------|:------------:|:------------------:|--------------------|-----------------|
| `translations.py` | 8 | 1 | 02 | V |
| Sidebar + workspace_sidebar + workspace JSON + fixtures | 9 | 4 | 02 ✅ | V |
| Labels JSON DocTypes (campo Link/Data) | 21 | 15+ | 03–05 | V |
| Hub `legal_case.json` + `case_hub.js` | 6 | 2 | 06 | A |
| Painel `public/js/painel/*` | 6 | 4 | 07 | A |
| `adv_case_nav.js` | 2 | 1 | 02 | A |
| Textos de ajuda / tooltips financeiros | 0 implementados | 5+ | 08–09 | A |
| Notificações (subject/body EN) | 2 | 1 | 10+ | A |
| Relatório label “Horas por Serviço” | 1 | 2 | 02 | V |

**Total divergências acionáveis:** 47 (excl. VM e conformes).

---

## Débitos Técnicos Identificados

| ID | Descrição | Severidade | Etapa sugerida |
|----|-----------|------------|----------------|
| DT-01 | Dois mapas de labels (`translations.py` e `adv_case_nav.DOCTYPE_NAV_LABELS`) divergem e duplicam manutenção | Média | 03 — unificar fonte |
| DT-02 | Notificação `Advocacia - Hearing amanha` com subject/body em inglês (“Hearing amanha”, “Court Branch”) | Baixa | Backlog |
| DT-03 | Custom Fields Event (`Source DocType`, `Source Name`) visíveis ao admin — fora do glossário jurídico | Baixa | Backlog |
| DT-04 | `manual_usuario.md` e `generate_manual.py` ainda usam “Serviço”, “Pagamento”, nomes EN de DocType | Média | 11 (docs) |
| DT-05 | Inconsistência sidebar “Fluxo de Caixa” vs workspace “Fluxo de Caixa Projetado” | Baixa | ~~02~~ **Resolvido Etapa 03** |
| DT-06 | Nenhum texto de ajuda financeiro obrigatório (§ glossário) implementado nos forms/hub | Alta | 08–09 |

---

## Mudanças Rejeitadas

### Renomear DocType `Legal Payment` → `Receipt`
**Motivo da rejeição:** Risco crítico. Quebra financial.py, hooks, permissions, testes e dados em `tabLegal Payment`.

### Renomear DocType `Legal Case` → `Lawsuit` ou equivalente
**Motivo da rejeição:** Risco crítico. Hub, controllers, hooks, permissions, 12+ DocTypes satélite com Link.

### Renomear rota do painel
**Motivo da rejeição:** Quebra bookmarks, breadcrumbs, módulos dashboard.

### Traduzir placeholders Word
**Motivo da rejeição:** Invalida todos os templates `.docx` em produção.

### Renomear Roles
**Motivo da rejeição:** Impacta permissions, reports, fixtures, usuários atribuídos.

---

## Checklist de Segurança

- [x] Nenhum DocType EN alterado
- [x] Nenhum Role alterado
- [x] Nenhum Report Slug alterado
- [x] Nenhuma rota alterada
- [x] Nenhum placeholder Word alterado
- [x] Nenhum schema alterado
