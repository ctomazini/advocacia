# Modernização UX - App Advocacia

Documento permanente de acompanhamento do projeto de modernização de experiência do usuário.

**Criado:** 2026-06-09
**Última atualização:** 2026-06-23 (Etapa 09 encerrada; release **v1.1.0**)
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

**Próximas etapas:** Etapa 06 concluída — ver registro abaixo; implementação Etapas 07–09

---

### Etapa 06 — Auditoria UX pós-estabilização de linguagem

**Status:** Concluída
**Data:** 2026-06-22
**Branch:** `ux/step-05-yellow-risk-adjustments`
**Responsável:** Sessão Agent / projeto Advocacia
**Commit:** `[UX-STEP-06] Docs: UX audit post-language-stabilization`

**Objetivo:** Reavaliar o sistema como um todo após Etapas 03–05 (glossário aplicado). Gerar backlog priorizado de melhorias de formulário, onboarding e polimento. **Somente análise** — zero implementação.

**Pré-requisitos confirmados:**
- Etapa 03 concluída e commitada (`3816ee1` … `5dfb494`) — labels verdes aplicados
- Etapa 04 concluída — 314 testes OK, AUD-001–011 catalogados
- Etapa 05 concluída — AUD-001, 003, 004, 005, 011 resolvidos; 314 testes OK

**Método:** Leitura de código (`*.json`, `*.js`, `case_hub.js`, `adv_case_nav.js`, `painel/*`, `sidebar.py`, `audit_usability.md`, `audit_form_layout.md`). Validação visual no browser **não executada** (mesmo bloqueio da Etapa 04); conclusões baseadas em contrato código + auditorias existentes.

#### Auditoria por fluxo

##### Fluxo 1 — Novo cliente

| Critério | Achado |
|----------|--------|
| Cliques do painel até salvar | **2 cliques** até o formulário (Painel → chip Cliente → Salvar após preencher). Sidebar: **3+** (Advocacia → Clientes → +). |
| Campos obrigatórios claros | **Parcial.** `person_type` + `client_name` `reqd`; CPF/CNPJ via `mandatory_depends_on` (exigido no save, não asterisco fixo desde o início). Quick entry cobre tipo, nome e documento. |
| CPF/CNPJ desde o início | **Sim** no quick entry e save (validação `validators.py`). Máscaras em `masks.js`. |
| Próximo passo sugerido | **Ausente.** `client.js` só máscaras; sem CTA pós-save (“Cadastrar processo para este cliente?”). Connections Frappe existem mas não guiam estagiário. |
| Lista Frappe intimida | **Risco médio** para estagiário: list view padrão Frappe com filtros (`list_filters.js` ajuda no desktop). `hide_name_column` + `title_field` melhoram legibilidade. |

##### Fluxo 2 — Novo processo

| Critério | Achado |
|----------|--------|
| “Processo” consistente | **Sim** pós-Etapa 03: sidebar “Processos”, satélites Link “Processo”, painel chip “Processo”, hub abas em PT. Residual: prefixo técnico `SERV-` no `autoname` (intocável). |
| Cadastros auxiliares barreira dia 1 | **Sim, moderado.** Comarca/Vara/Tribunal em Cadastros (`keep_closed: 1`). Links no form **não obrigatórios** (`reqd: 0`). Consultoria/Diligência dispensam CNJ e cadastros judiciais. |
| Abas no primeiro save | **6 abas** visíveis após save: Detalhes, Andamento, Financeiro, Prazos e Tarefas, Comunicações e Registro de Horas, Documentos. **Pode assustar** estagiário; Detalhes concentra campos editáveis. |
| CNJ depois | **Sim** — `case_number` `reqd: 0`; `validate()` aceita vazio. Description JSON explica legado/CNJ. **Sem banner/intro** comunicando “pode preencher depois”. |
| Breadcrumb título vs ID | **Mostra ID** (`SERV-2026-…`). `adv_case_nav.js` `build_case_crumb` usa `case_name`; `build_form_crumb` usa `doc.name`. `get_case_title()` existe mas **não** é usado no breadcrumb. |

##### Fluxo 3 — Nova audiência

| Critério | Achado |
|----------|--------|
| Caminhos de criação | **4+:** (1) hub processo `+ Audiência` (prefill `legal_case`+`client`) — **recomendado**; (2) sidebar Audiências; (3) painel chip Audiência (sem prefill); (4) list Audiências + Add; (5) calendário (`hearing_calendar.js`). |
| Órfã sem processo | **Bloqueada no save** — `legal_case` `reqd: 1`. Sidebar/painel permitem abrir form vazio → erro no save (fricção, não dado órfão). |
| Quick entry | **Suficiente** para operação: Processo, Data/Hora, Tipo. Modalidade/Vara ficam no form completo. Description cliente ainda diz “serviço” (legado textual). |

##### Fluxo 4 — Prazo vs Tarefa

| Critério | Achado |
|----------|--------|
| Distinção clara | **Conceitual no glossário**; na UI só via labels e descriptions (“Data fatal do prazo processual” vs “Prazo para conclusão da tarefa (opcional)”). |
| Hub | Aba **Prazos e Tarefas** com painéis HTML separados (`deadlines_panel`, `tasks_panel`). |
| Painel | Chips distintos; KPIs separados (`prazos_urgentes` vs `legal_tasks_pendentes`); timeline badge “Prazo” / “Tarefa”. |
| Orientação secretária | **Insuficiente.** Sem intro, empty state comparativo ou wizard. `Legal Task.legal_case` **opcional** — tarefa pode existir sem processo (diferente de `Deadline`). |

##### Fluxo 5 — Contrato de honorários → Recebimentos

| Critério | Achado |
|----------|--------|
| Fluxo explicado na UI | **Não** — intro obrigatória (§ glossário) **não implementada** (AUD-002). |
| Tooltip “Gerar Parcelas” | **Ausente** — Button `generate_installments`; DEC-F04 pendente. |
| Onde ver parcelas | Grid no Fee Agreement (coluna Recebimento clicável); hub aba Financeiro (`installments_panel`, `payments_panel`); lista Recebimentos (`legal_payment_list.js` coluna Origem). |
| Sucumbência / divisão | Lógica em `fee_agreement.js` (`Honorários Diretos` vs `Acordo com Divisão`); descriptions por campo. **Não autoexplicativo** para secretária — prompt sucumbência só após Gerar Parcelas no modo divisão. |

##### Fluxo 6 — Cobrança de serviço avulso

| Critério | Achado |
|----------|--------|
| Diferença Fee Agreement | **Não explicada in-app** (DEC-F02 pendente). Nomes distintos pós-Etapa 03 ajudam. |
| Tooltip “Sincronizar Cobrança” | **Ausente no botão**; dialog de sync traz texto útil (`sync_hint`). |
| Onde aparece resultado | Botão “Ver recebimento”; hub Serviços Avulsos + KPI “A faturar”; lista Recebimentos filtrável. |

##### Fluxo 7 — Custas processuais

| Critério | Achado |
|----------|--------|
| Custa vs Despesa Escritório | **Estruturalmente separados** (DEC-F05). Menu: Custas em Gestão de Casos; Despesas em Financeiro. |
| Campo “quem arca” | **Parcial.** `bill_to_client` (Check “Repassar ao Cliente”) — não Select Escritório/Cliente do glossário. Default `1`. |
| Reembolso documentado | `transfer_date` + descriptions; **sem intro** de fluxo reembolso na UI. |

##### Fluxo 8 — Financeiro consolidado do processo

| Critério | Achado |
|----------|--------|
| Aba Financeiro clara | **Parcial.** `_adv_hub_render_financial_summary` com 5 KPIs + barra % recebido + hint curto. Falta banner normativo (AUD-002). |
| Quantos painéis | **5 blocos:** Resumo, Recebimentos de Honorários, Recebimentos, Custas, Serviços Avulsos (este último em section própria). Não competem, mas **densidade alta**. |
| “Quanto falta receber” | KPIs separados: `total_pending_honorarios`, `total_services_unbilled`, `total_pending_service_payments`. Usuário **precisa somar mentalmente** — sem total único “a receber deste processo”. |

#### Auditoria de formulários (standalone)

Cobertura de descriptions: **94%** (218/232) — `audit_usability.md`. Tooltips = campo `description` no JSON.

| DocType | Seções lógicas | Tooltips | Obrigatórios primeiro | Tabs adequadas | Descrições |
|---------|:--------------:|:--------:|:-----------------------:|:--------------:|:----------:|
| Legal Case | ✅ hub 6 abas | ✅ ~22 | ✅ Cliente+Tipo | ✅ por domínio | ✅ falta intro CNJ/financeiro |
| Fee Agreement | ✅ Valores/Parcelas/Sucumbência | ✅ 37 | ✅ Processo+Cliente | N/A (form longo) | ✅ falta intro fluxo |
| Legal Payment | ✅ Origem/Controle | ✅ 18 | 🟡 origem auto | N/A | ✅ intro só se Cancelado |
| Service Record | ✅ Atos/Cobrança/Totais | ✅ 22 | ✅ Processo | N/A | ✅ falta intro vs honorários |
| Hearing | ✅ Info/Detalhes/Obs | ✅ 17 | ✅ Processo+Data+Tipo | N/A | ✅ desc. cliente legado |
| Deadline | ✅ referência layout | ✅ 16 | ✅ Processo+Data+Desc | N/A | ✅ |
| Legal Task | ✅ Info/Detalhes | ✅ | 🟡 Processo opcional | N/A | ✅ |
| Court Cost | ✅ Info/Valores/Controle | ✅ | ✅ Processo+Tipo+Valor | N/A | ✅ falta intro reembolso |
| Case Communication | ✅ | ✅ | ✅ Processo | N/A | ✅ |
| Time Entry | ✅ | ✅ 16 | 🟡 | N/A | ✅ |
| Case Document | ✅ | ✅ | ✅ Processo | N/A | ✅ |
| Office Expense | ✅ | ✅ | ✅ campos core | N/A | ✅ |
| Client | ✅ PF/PJ/Contatos | ✅ 16 | ✅ Tipo+Nome+doc | N/A | ✅ |

#### Notas por persona

**Advogado titular**
- Glossário financeiro (Recebimento vs Custa vs Despesa) **correto pós-Etapa 05**; falta texto de ajuda nos forms para sucumbência/divisão.
- Hub Financeiro entrega KPIs úteis; quer total consolidado “a receber” em um número.
- CNJ opcional e cadastros rígidos alinhados à prática; breadcrumb com ID é aceitável.

**Secretária jurídica**
- Painel + chips aceleram cadastros; **Fee Agreement** e sync de cobrança ainda exigem treinamento oral.
- **Prazo vs Tarefa** — maior risco operacional: nomes similares, tarefa sem processo permitida.
- Quick entries de Cliente/Processo/Audiência/Prazo são adequados; Fee Agreement sem quick entry (form completo).

**Estagiário (primeiro dia)**
- 6 abas do processo + lista Frappe padrão = **curva íngreme**; sem onboarding in-app.
- Sem CTA pós-cliente → processo; audiência pelo painel abre form sem processo (erro no save).
- Tooltips (descriptions) ajudam ao passar mouse, mas estagiário não descobre sozinho o fluxo honorários→parcelas→recebimentos.

#### Backlog priorizado — pós-Etapa 06

| Prioridade | ID | Item | Área | Esforço | Etapa sugerida |
|:----------:|:---|:-----|:-----|:--------|:--------------|
| **P0** | UX-06-001 | Textos de ajuda financeiros obrigatórios (banner hub Financeiro + intros Fee Agreement, Service Record, Legal Payment, Court Cost) | Hub + forms | M | **08** |
| **P0** | UX-06-002 | Tooltips botões “Gerar Parcelas” e “Sincronizar Cobrança” (DEC-F04) | Forms JS | S | **08** |
| **P0** | UX-06-003 | Orientação Prazo vs Tarefa (intro aba hub, empty states ou bloco HTML comparativo) | Hub + forms | M | **07** |
| **P0** | UX-06-004 | Breadcrumb hub/satélites: exibir `title` (`ID — Cliente`) em vez de só `SERV-…` | `adv_case_nav.js` | S | **07** |
| **P1** | UX-06-005 | CTA pós-save Cliente: “Cadastrar processo para este cliente” | `client.js` | S | **07** |
| **P1** | UX-06-006 | Chip Audiência/Prazo no painel: prefill último processo ou aviso “selecione o processo no hub” | Painel | S | **07** |
| **P1** | UX-06-007 | Intro processo novo: CNJ opcional + cadastros judiciais podem wait | `legal_case.js` | S | **07** |
| **P1** | UX-06-008 | KPI hub “Total a receber neste processo” (honorários pendentes + serviços avulsos) | `case_hub.js` + backend | M | **08** |
| **P1** | UX-06-009 | Hub pills: revisar singular vs plural (AUD-006) | `case_hub.js` | S | **07** |
| **P1** | UX-06-010 | Dashboard Legal Case: grupos “Contratos de Honorários” (AUD-007) | `legal_case_dashboard.py` | S | **07** |
| **P1** | UX-06-011 | Aba Horas: alinhar “Horas Trabalhadas” vs “Registro de Horas” (AUD-008) | `legal_case.json` | S | **07** |
| **P1** | UX-06-012 | Aviso soft quando Legal Task salva sem processo | `legal_task.js` | S | **07** |
| **P2** | UX-06-013 | Onboarding primeiro acesso (workspace card ou tour painel) | Workspace/Painel | L | **09** |
| **P2** | UX-06-014 | Court Cost: label/glossário “Responsável pela Custa” (Escritório/Cliente) vs check | `court_cost.json` | M | **09** |
| **P2** | UX-06-015 | Corrigir descriptions legadas “serviço” em Hearing/Deadline/Legal Task | JSON | S | **09** |
| **P2** | UX-06-016 | `fee_agreement.js`: mensagens hardcoded sem `__()` | JS | S | **09** |
| **P2** | UX-06-017 | Manual / `generate_manual.py` termos legados (AUD-010 / DT-04) | Docs | M | **11** |
| **P2** | UX-06-018 | Completar 14 descriptions restantes (campos técnicos) | JSON/script | S | **09** |

**Mapeamento AUD/DT → UX-06:** AUD-002 → UX-06-001/002; AUD-006 → UX-06-009; AUD-007 → UX-06-010; AUD-008 → UX-06-011; DT-06 → UX-06-001; DT-04 → UX-06-017.

**Testes:** Nenhum (auditoria read-only).

**Próximas etapas:** Projeto **ENCERRADO** — ver `docs/ux-final-executive-report.md`.

---

### Etapa 09 — Polimento final e encerramento

**Status:** Concluída — **PROJETO ENCERRADO**
**Data:** 2026-06-22
**Branch:** `ux/step-09-final-polish`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Refinar empty states do hub, descriptions de listas vazias, list views com indicadores, itens AUD cosméticos, manual do usuário e documentação de encerramento. Sem alterar lógica de negócio, schema, permissões ou relatórios.

**Pré-requisitos confirmados:** Etapa 08 commitada (`cbd508c`).

#### Commits

| Entrega | Escopo |
|---------|--------|
| Hub empty states | `_adv_hub_empty` com título + hint + CTA; 9 painéis; CSS `.adv-hub-empty__title/hint` |
| List descriptions | 10 DocTypes com `description` amigável na list view |
| List views | Legal Task, Deadline, Hearing — indicadores de status/urgência/data |
| AUD cosméticos | Legal Case connection groups; aba Horas; fee_agreement `__()`; Kanban labels; print formats |
| Manual | `manual_usuario.md` — glossário, Processos, fluxo financeiro, documentos Word |
| Encerramento | `ux-final-executive-report.md`, `audit_usability.md`, roadmap ENCERRADO |

#### Testes

| Comando | Resultado |
|---------|-----------|
| `bench --site advocacia.local migrate` | OK |
| `bench --site advocacia.local run-tests --app advocacia` | **314 OK** |

#### Checklist de segurança final

- [x] Sem renomeação de DocTypes EN
- [x] Sem alteração de Roles
- [x] Sem alteração de slugs de relatórios
- [x] Sem alteração de rotas
- [x] Sem alteração de placeholders Word
- [x] Sem alteração de schema / fieldnames
- [x] Sem alteração de child tables
- [x] Sem `frappe.db.commit()` novo em handlers/API
- [x] Suíte de testes verde

#### Pendências documentadas (pós-projeto)

Ver `docs/ux-final-executive-report.md` §6 — UX-06-004, UX-06-008, UX-06-009, UX-06-017/018, AUD-009.

**Relatório executivo:** [ux-final-executive-report.md](./ux-final-executive-report.md)

---

### Etapa 08 — Onboarding e experiência inicial

**Status:** Concluída
**Data:** 2026-06-22
**Branch:** `ux/step-08-onboarding`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Melhorar onboarding reutilizando componentes existentes (empty states, pills, banners). Jornada inicial no painel, quick actions simplificadas, card workspace, checklist do processo no hub e banner narrativo financeiro. Sem novos endpoints, alteração de schema, permissões ou lógica financeira.

**Pré-requisitos confirmados:** Etapa 07 commitada (`1febcaf`).

#### Commits

| Entrega | Escopo principal |
|---------|------------------|
| Dashboard onboarding | Jornada 3 passos quando `list_meta.active_cases.total === 0`; KPIs/charts ocultos; quick actions filtradas (+ Cliente, + Processo, + Prazo, + Audiência); chips com prefixo `+`; mensagem financeira para Advocacia User |
| Workspace Comece Aqui | Card no grid com header explicativo + atalhos Clientes, Painel, Processos (`advocacia.json` + fixture) |
| Hub checklist | Checklist honorários/prazo/audiência (judicial) na barra de resumo; CTAs `+`; some quando completo |
| Hub banner financeiro | Banner restrito (User) e narrativa receita (Manager) na aba Financeiro |

#### Entregas implementadas

| Área | Detalhe |
|------|---------|
| Painel | `painel_is_onboarding`, `render_onboarding_journey`, `render_financial_restricted` em `hero.js`; branch onboarding em `main.js`; CSS `.painel-onboarding-*` |
| Workspace | Seção **Comece Aqui** no topo do grid (sem sidebar) |
| Hub | `_adv_hub_render_case_checklist`, `_adv_hub_finance_narrative_banner`; estilos `.adv-hub-checklist-*` |
| Perfil User | Zona financeira do painel + aba Financeiro do hub com mensagem Gestor |

#### Testes

| Comando | Resultado |
|---------|-----------|
| `bench --site advocacia.local migrate` | OK |
| `bench --site advocacia.local run-tests --app advocacia` | **314 OK** (311 + 3 sidebar) |

#### Pendências remanescentes (Etapa 09+)

- UX-06-004 breadcrumb title
- UX-06-008 KPI “Total a receber neste processo”
- UX-06-009–011 hub pills polish, dashboard grupos

**Próximas etapas:** Etapa 09 — polish UX-06-004/008/009 + avisos operacionais

---

### Etapa 07 — Organização de formulários

**Status:** Concluída
**Data:** 2026-06-22
**Branch:** `ux/step-07-form-organization`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Melhorar agrupamentos, seções, tooltips, descriptions e intros dos formulários prioritários (backlog UX-06-001/002 parcial + UX-06-003/007). Sem alterar fieldnames, schema de dados, child tables, relacionamentos ou lógica de sync.

**Pré-requisitos confirmados:** Etapa 06 commitada (`1807b8d`).

#### Commits (um por formulário)

| Formulário | Commit | Escopo principal |
|------------|--------|------------------|
| Legal Case | `2775d3e` | Seção Partes, column break, reorder Detalhes, tooltips CNJ/cadastros, intro CNJ opcional |
| Fee Agreement | `22d0565` | `field_order` fluxo Vínculo→Valores→Parcelas, intro + tooltip Gerar Parcelas/Sucumbência |
| Legal Payment | `600d510` | Reorder Vínculos→Financeiro→Comprovante→Sync (colapsável) + intro |
| Service Record | `45ad74e` | Intro vs honorários, tooltip Sincronizar Cobrança, description list view DocType |
| Hearing | `d583fb1` | Reorder data/tipo primeiro, tooltips link virtual e cliente |
| Deadline | `e499fff` | `due_date` destacado, intro Prazo vs Tarefa, tooltip notificação (`deadline.js` novo) |
| Court Cost | `284b4f7` | Reorder tipo→valor→reembolso, intro custas, descriptions quem arca |
| Legal Task | `8e92d10` | Reorder campos operacionais, intro diferenciação vs Prazo |

**Commit roadmap:** `[UX-STEP-07] Docs: update modernization roadmap`

#### Textos de ajuda financeiros implementados

| DocType | Intro JS | Tooltips JSON |
|---------|:--------:|:-------------:|
| Fee Agreement | ✅ | ✅ Gerar Parcelas, Sucumbência (section) |
| Service Record | ✅ | ✅ Sincronizar Cobrança (button description) |
| Legal Payment | ✅ | — (campos existentes) |
| Court Cost | ✅ | ✅ Repassar ao Cliente / reembolso |

#### Formulários reorganizados

- `Legal Case` — aba Detalhes: Cliente/Tipo → Dados do Processo → Partes → Observações (colapsável)
- `Fee Agreement` — Vínculo → Valores → Sucumbência → Parcelamento → Parcelas → Totais → Obs
- `Legal Payment` — Relacionamentos → Financeiro → Controle (comprovante) → Sincronização (colapsável)
- `Service Record` — Vínculo → Atos → Totais → Cobrança → Obs
- `Hearing` — Processo/Data/Tipo → Detalhes/modalidade → Obs
- `Deadline` — Processo/Data fatal/Descrição → Detalhes → Obs
- `Court Cost` — Identificação → Valores e Reembolso → Controle
- `Legal Task` — Vínculo + operação → Detalhes (texto)

#### Testes

| Comando | Resultado |
|---------|-----------|
| `bench --site advocacia.local migrate` | OK |
| `bench --site advocacia.local run-tests --app advocacia` | **314 OK** (311 + 3 sidebar) |

#### Pendências remanescentes (Etapa 08+)

- UX-06-004 breadcrumb title (fora do escopo forms-only)
- UX-06-008 KPI “Total a receber neste processo” (hub backend)
- UX-06-009–012 hub pills, dashboard grupos, aviso Legal Task sem processo no save
- Banner normativo aba Financeiro do hub (`case_hub.js` — proibido nesta etapa)

**Próximas etapas:** Etapa 08 — banner hub Financeiro + KPI consolidado + polish UX-06-004/008

---

### Etapa 04 — Auditoria pós-mudanças verdes

**Status:** Concluída
**Data:** 2026-06-09
**Branch:** `ux/step-03-green-risk-labels` (auditoria read-only sobre commits Etapa 03)
**Responsável:** Sessão Agent / projeto Advocacia
**Commit:** `[UX-STEP-04] Docs: post-green audit results` (branch `ux/step-03-green-risk-labels`)

**Objetivo:** Garantir que labels verdes da Etapa 03 não introduziram regressões (testes, sidebar, traduções, relatórios, permissões). Somente leitura — zero implementação.

**Pré-requisitos confirmados:**
- Etapa 03 commitada (`3816ee1` … `599b518`)
- `bench --site advocacia.local migrate` executado antes da auditoria

#### Validações automatizadas

| # | Verificação | Resultado |
|---|-------------|-----------|
| 1 | `run-tests --app advocacia` | **314 OK** (311 + 3 `test_sidebar_json`) |
| 2 | `test_sidebar_json` isolado | Incluído no suite completo — OK *(execução isolada falhou por lock DB concorrente; suite completa passou)* |
| 3 | Sidebar no banco (`tabWorkspace Sidebar Item`, parent=Advocacia) | **33 itens** (5 seções + 28 links) — labels alinhados ao glossário |
| 4 | Traduções DocType no banco (pt + pt-BR) | **23 pares** × 2 idiomas = 46 registros — todos batem com `DOCTYPE_LABELS` |
| 7 | Script reports (`execute` com filters vazios) | **6/6 OK** — produtividade, horas_por_servico, inadimplencia, fluxo_de_caixa, honorarios_por_cliente, carteira_ativa |
| 8 | Permissões `Advocacia User` / `Advocacia Manager` | **22 DocTypes** cada — CRUD conforme esperado (User sem delete em transacionais) |

#### Validações manuais (browser)

| # | Verificação | Resultado |
|---|-------------|-----------|
| 5 | Hub Legal Case (`SERV-2026-18425`) | **Não executado** — servidor web indisponível no ambiente de auditoria (`chrome-error` em `:8000`). Verificação substituta: labels em `legal_case.json` + `case_hub.js` conforme glossário §7 |
| 6 | Painel (`/app/painel`) | **Não executado** — mesmo bloqueio. Verificação substituta: `hero.js`, `kpis.js`, `financeiro.js` — chips Cliente/Tarefa/Recebimento OK; link “Ver recebimentos” corrigido na Etapa 05 (AUD-001) |

#### Sidebar no banco (links, pós-migrate)

Ordem idêntica a `SIDEBAR_LINK_ORDER`: Processos, Recebimentos, Contratos de Honorários, Cobranças de Serviço, Despesas do Escritório, Modelos de Documento, Horas por Processo, Fluxo de Caixa Projetado, Configurações do Escritório, etc.

#### Itens verificados sem problema (OK)

- Testes unitários/integração: **314 verdes**, sem regressão vs Etapa 03
- Paridade código ↔ JSON sidebar (`test_sidebar_json`)
- Sidebar DB ↔ `sidebar.py` ↔ `workspace_sidebar/advocacia.json`
- Seed de traduções DocType aplicado no banco (pt + pt-BR)
- Slugs de relatório intocados (`report_name` = slug EN)
- Relatórios executam sem exceção; colunas principais em PT (Processo, Cliente, Fase Processual)
- Permissões por role inalteradas
- Checklist de segurança Etapa 03 mantida (sem schema/DocType EN/rotas/placeholders)
- Hub JSON: abas Financeiro, Recebimentos de Honorários, Recebimentos, Serviços Avulsos, Horas Trabalhadas, Resumo do Processo
- Painel hero: chips Cliente, Processo, Tarefa, Recebimento, Despesa do Escritório

#### Problemas encontrados (AUD-XXX)

| ID | Severidade | Área | Problema | Causa / notas | Etapa sugerida |
|----|------------|------|----------|---------------|----------------|
| AUD-001 | ~~**Médio**~~ **Resolvido Etapa 05** | Forms + painel + backend | Mensagens/botões ainda usam “pagamento”, “Legal Payment” para **entrada** do cliente | Corrigido em `f817ff9` | ~~05~~ |
| AUD-002 | **Médio** | Hub + forms financeiros | Textos de ajuda obrigatórios (§ glossário) ausentes | DT-06 — banner Financeiro, intros Fee Agreement / Service Record / Legal Payment / Court Cost | **08–09** |
| AUD-003 | ~~**Baixo**~~ **Resolvido Etapa 05** | Arquitetura labels | `translations.py` e `adv_case_nav.DOCTYPE_NAV_LABELS` duplicados | Fonte única: `__(doctype)` + seed `translations.py` (`b0a6154`) | ~~05~~ |
| AUD-004 | ~~**Baixo**~~ **Resolvido Etapa 05** | Notificações | Subject/body EN: “Hearing amanha”, “Court Branch”, “servico” | `fixtures/notification.json` + scheduler audiências (`4879a4d`, `f817ff9`) | ~~05~~ |
| AUD-005 | ~~**Baixo**~~ **Resolvido Etapa 05** | Documentos hub | `documentos_generate_dialog.js`: “Salve o **serviço** antes…” | `9d148ae` | ~~05~~ |
| AUD-006 | **Baixo** | Hub pills | Pills usam `_nav_label()` → plural de lista (“Tarefas”, “Recebimentos”) | By design para atalho de lista; singular só em chips do painel | Aceitar ou **06** |
| AUD-007 | **Baixo** | Dashboard Legal Case | Grupos de links ainda “Honorários” (não “Contratos de Honorários”) | Widget Frappe dashboard — baixa visibilidade | **06** |
| AUD-008 | **Baixo** | Hub aba Horas | Section “Horas Trabalhadas” vs painel “Registro de Horas” | Dois conceitos próximos no mesmo tab | **06** |
| AUD-009 | **Baixo** | Relatório fluxo_de_caixa | Coluna oculta “Origem DocType” expõe EN | Campo técnico de Dynamic Link | Backlog |
| AUD-010 | **Baixo** | Manual | `generate_manual.py` / manual ainda com “Serviço”, “Pagamento” | DT-04 | **11** |
| AUD-011 | ~~**Baixo**~~ **Resolvido Etapa 05** | Fee Agreement form | Botão “Re-sincronizar **Legal Payments**” | `1f85151` | ~~05~~ |

**Críticos:** nenhum (testes verdes, permissões OK, sidebar/traduções OK).

#### Backlog priorizado — Etapa 06+

| Prioridade | Item | AUD / DT |
|------------|------|----------|
| ~~P1~~ | ~~Mensagens e botões: pagamento/Legal Payment → recebimento~~ | ~~AUD-001, AUD-005, AUD-011~~ **Etapa 05** |
| ~~P2~~ | ~~Unificar mapa de labels~~ | ~~AUD-003 / DT-01~~ **Etapa 05** |
| P3 | Textos de ajuda financeiros (banner hub + intros forms + tooltips DEC-F04) | AUD-002 / DT-06 |
| P4 | Hub/dashboard polish (grupos dashboard, pills singular/plural, aba Horas) | AUD-006–008 |
| ~~P5~~ | ~~Notificações PT~~ | ~~AUD-004 / DT-02~~ **Etapa 05** |
| P6 | Manual e docs operacionais | AUD-010 / DT-04 |

**Próximas etapas:** Etapa 06 concluída — backlog UX-06-001+; implementação Etapas 07–09

---

### Etapa 05 — Ajustes amarelos pós-auditoria

**Status:** Concluída
**Data:** 2026-06-09
**Branch:** `ux/step-05-yellow-risk-adjustments`
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Resolver backlog P1/P2/P5 da Etapa 04 — mensagens de feedback UI (pagamento → recebimento), fonte única de labels DocType no JS, notificações PT.

**Política DEC-F01:** strings user-facing de entrada (`Legal Payment`) → **Recebimento**; manter “pagamento” em saída (`Court Cost`, `Office Expense`).

**Commits (um por AUD):**

| AUD | Commit | Descrição |
|-----|--------|-----------|
| AUD-005 | `9d148ae` | Dialog documentos: “Salve o **processo** antes…” |
| AUD-011 | `1f85151` | Fee Agreement: botão/confirm “Re-sincronizar **Recebimentos**” |
| AUD-001 | `f817ff9` | Forms + painel + backend: mensagens recebimento (Legal Payment, pagamento) |
| AUD-003 | `b0a6154` | Remove `DOCTYPE_NAV_LABELS`; `get_doctype_label` → `__(doctype)` |
| AUD-004 | `4879a4d` | Fixtures notification: processo, audiência, vara, recebimento vencido |

**Arquivos principais:** `legal_payment.*`, `service_record.*`, `financeiro.py`, `painel/financeiro.py`, `tasks.py`, `public/js/painel/*`, `adv_case_nav.js`, `fixtures/notification.json`.

**AUD resolvidos nesta etapa:** AUD-001, AUD-003, AUD-004, AUD-005, AUD-011.

**Testes:** **314 OK** (`bench --site advocacia.local run-tests --app advocacia`).

**Validação:** `bench build --app advocacia` + `migrate` (sync fixtures Notification).

**Pendências:** AUD-002 (textos de ajuda financeiros, Etapa 08); AUD-006–008 (catalogados na Etapa 06 → UX-06-009–011); AUD-009–010 (backlog / Etapa 11).

**Próximas etapas:** Etapa 06 concluída — ver backlog UX-06; implementação Etapas 07–09

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
| 3b | `5dfb494` | Labels restantes: Office Expense, Service Record, Horas Trabalhadas |
| 4 | — | Deduplicação sidebar: **não necessária** (Etapa 01 confirmou 28 links únicos) |

**Arquivos principais:** `setup/translations.py`, `setup/sidebar.py`, `workspace_sidebar/advocacia.json`, `workspace/advocacia/advocacia.json`, `fixtures/workspace.json`, `adv_case_nav.js`, `case_hub.js`, `public/js/painel/*`, 20+ JSON de DocTypes, `add_field_descriptions.py`, relatórios (labels em `.py`/`.js`).

**DIV resolvidas (V + hub/painel tocados):** DIV-001–DIV-009, DIV-011–DIV-035, DIV-036–DIV-038, DIV-040–DIV-046, DIV-047 *(resolvido Etapa 05 — DT-01)*.

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
| DT-01 | ~~Dois mapas de labels~~ — fonte única via `translations.py` + `__(doctype)` no JS | ~~Média~~ **Resolvido Etapa 05** | `b0a6154` |
| DT-02 | ~~Notificação EN~~ — fixtures e scheduler audiências em PT | ~~Baixa~~ **Resolvido Etapa 05** | `4879a4d` |
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

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
