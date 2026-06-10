# Auditoria Deploy-Ready — Advocacia

> **Snapshot histórico** (v0.7.0, jun/2026). Estado atual: [README.md](./README.md), [audit_code.md](./audit_code.md), [audit_dashboard.md](./audit_dashboard.md). **Suíte atual: 283 testes OK.**

**Data:** 2026-06-02  
**Commit:** `3810cb0` — feat: office settings, IA, placeholders, painel/reports e docs v1.0.0  
**Site auditado:** `advocacia.local` (bench nativo, Frappe v16)  
**Versão app:** 1.0.0 (`pyproject.toml`)  
**Critério:** padrão unificado `REGRAS_OBRIGATORIAS.md` (engenharia), com notas brownfield de `REGRAS_ADVOCACIA.md`

---

## Resumo

| Status | Quantidade | Interpretação |
| --- | ---: | --- |
| ✅ Passou | **42** | Conformidade plena ou aceitável para produção |
| ⚠️ Atenção | **14** | Débito técnico / risco moderado — corrigir pós-go-live ou antes se possível |
| ❌ Bloqueante | **0** | Nenhuma violação crítica impede deploy imediato |

**Veredito:** o app está **apto para deploy** em bench nativo, desde que o site de produção seja instalado via `install-app` + `migrate` (não cópia ad hoc do banco de dev). Itens ⚠️ devem entrar no backlog pós-deploy.

**Suíte de testes (executada nesta auditoria):** `241` testes, **OK** (`bench --site advocacia.local run-tests --app advocacia`).

---

## Débito Técnico Histórico (resolvido ou congelado)

| Item histórico | Status jun/2026 |
| --- | --- |
| DocTypes em português (`Servico`, `Audiencia`, …) | ✅ **Resolvido** — v1.0.0 renomeou 24 DocTypes para EN |
| Server Scripts / Client Scripts no banco | ✅ **Zero** em `advocacia.local` |
| `custom: 1` em DocTypes do app | ✅ **Zero** |
| `frappe.db.commit()` em handlers de request/scheduler | ✅ **Removido** de `documentos`, `painel`, `financeiro`, `tasks`, `notificacoes` |
| `agent_api.py` inexistente | ✅ **Implementado** (4 endpoints + 10 testes) |
| Painel JS monolítico (>3000 linhas) | ✅ **Modularizado** — `public/js/painel/` (~2.490 linhas, 14 módulos + `main.js`) |
| Nomes PT congelados (decisão REGRAS v0.6) | ⚠️ **Supersedido** por v1.0.0 EN — documentar para equipe |

---

## Detalhamento por Seção

### SEÇÃO 1 — DocTypes: Schema e Naming

#### 1.1 `custom: 0`
✅ **Zero** ocorrências de `"custom": 1` em `advocacia/advocacia/doctype/*/`.

#### 1.2 `naming_rule` + `autoname`
✅ **19 standalones** com `naming_rule` explícito.

| Padrão | DocTypes |
| --- | --- |
| `format:PREFIX-{YYYY}-{####}` | Legal Case, Client, Fee Agreement, Legal Payment, Hearing, Deadline, Legal Task, Service Record, Court Cost, Office Expense, Time Entry, Case Communication |
| `By fieldname` | Jurisdiction, Court Branch, Court, Case Phase, Document Template, Document Kit |
| `Expression` (Single) | Office Settings → `Office Settings` |

⚠️ Auxiliares usam `field:*_name` (padrão Frappe para cadastro rígido) — aceitável.

#### 1.3 `title_field` + `show_title_field_in_link`
✅ **18/19** standalones com `title_field` definido e `show_title_field_in_link=1`.

⚠️ **Office Settings:** `title_field` ausente — aceitável para Single institucional; recomendado `razao_social` no backlog.

#### 1.4 `search_fields`
✅ **18/19** standalones com `search_fields`.

⚠️ **Office Settings:** `search_fields` ausente — aceitável para Single raramente buscado.

#### 1.5 DocType names — idioma
✅ **24 DocTypes** em inglês Title Case Singular: `Legal Case`, `Client`, `Office Settings`, `Fee Agreement`, etc.

> Nota: o prompt original esperava nomes PT como ❌; a migração v1.0.0 **já fechou** este débito.

#### 1.6 Fieldnames — qualidade
⚠️ **13 `column_break_*` auto-gerados** (Frappe UI) — cosmético, sem impacto funcional.

⚠️ Fieldnames mistos EN/PT residuais (`titulo` em Document Template/Kit, `nome` em Client, `razao_social` em Office Settings) — **congelado** por decisão brownfield; backlog v2.

✅ **Zero** fieldnames com acentos portugueses.

#### 1.7 Link fields tipados
✅ **Zero** suspeitas reais de `Data` usado como Link.

Falsos positivos do grep (`case_phase_name`, `court_name`, …) são campos **nome legível** de auxiliares com autoname `field:`, não referências.

#### 1.8 Prefixos autoname — colisão
✅ **12 prefixos únicos**, cada um com contagem 1 — sem colisão.

#### 1.9 `idx` duplicado
✅ **Zero** duplicatas detectadas (incl. Service Record — corrigido em ciclo anterior).

---

### SEÇÃO 2 — Controllers Python

#### 2.1 Ordem do ciclo de vida
✅ Controllers seguem padrão `validate()` → hooks auxiliares; sem inversões críticas detectadas.

#### 2.2 Auto-título no controller
✅ Títulos compostos via `titulos.py` (`aplicar_titulo_pos_insert`) em Legal Case, Legal Payment, Hearing, Deadline, Legal Task, Service Record, Court Cost, Time Entry, Case Communication, Fee Agreement, etc. — **não** via Server Script.

#### 2.3 `frappe.db.commit()` proibido
✅ **Zero** em paths quentes: `documentos.py`, `painel/`, `financeiro.py` (handlers), `tasks.py`, `notificacoes.py`, `agent_api.py`, `calendar_sync.py`.

⚠️ **`commit()` remanescente (aceitável com ressalvas):**

| Arquivo | Contexto |
| --- | --- |
| `setup/*` | `after_install`, `after_migrate`, permissions, sidebar, reports, translations — com comentários |
| `titulos.py` | `backfill_titulos_vazios()` delega a `setup/titles.ensure_backfill_titles(commit=True)` — utilitário manual via `bench execute`, não hook automático |
| `setup/seed_demo.py`, `tests/*`, `e2e/*` | Dev/test only |

#### 2.4 `ignore_permissions`
⚠️ **~143 ocorrências** — maioria em `tests/` e `test_setup.py`.

✅ Produção documentada: `financeiro.py` (bloco comentário linhas 5–11), `calendar_sync.py`, `documentos.py` (File attach), `setup/seed_demo.py`.

#### 2.5 `except Exception: pass`
✅ **Zero** ocorrências.

#### 2.6 `eval` / `exec`
✅ **Zero** ocorrências.

#### 2.7 Strings sem `_()`
⚠️ **~25 hits** — maioria **falso positivo** (parâmetro `title=_("...")` em linha seguinte). Violações reais menores:

- `fee_agreement.js`: msgprints hardcoded PT sem `__()`
- `validators.py`: alguns `frappe.throw(` multilinha — verificar cobertura `_()` linha a linha

Não bloqueante para deploy backend; ⚠️ para i18n futura.

#### 2.8 Whitelisted — permission + type hints
✅ **26 funções** `@frappe.whitelist` em produção — **todas** com `frappe.has_permission(..., throw=True)`.

Lista principal: `agent_api` (4), `documentos` (4), `painel_api` (2), `financeiro` (6), DocType forms (timer, parcela, prazo, audiência, despesa, legal_case_query).

#### 2.9 N+1 queries
⚠️ **`agent_api.get_active_cases`:** loop com 3× `frappe.db.count` por caso (até 100 casos).

⚠️ **`painel/`:** agregações já refatoradas parcialmente; revisar loops residuais em `financeiro.py` (`get_doc` pontual, não em loop massivo).

Não bloqueante para volume típico de escritório; otimizar antes de escala MCP.

#### 2.10 `limit_page_length` em queries
⚠️ **~40 `get_all`/`sql`** sem `limit` explícito no grep — muitos em schedulers com filtros estreitos ou listas pequenas.

✅ `notificacoes.py`: `limit_page_length=500`  
✅ `documentos.py`: kits com `limit_page_length=0` comentado (kits pequenos)  
⚠️ Revisar `tasks.py` schedulers e `financeiro.py` bulk paths.

---

### SEÇÃO 3 — JavaScript Client-Side

#### 3.1 `cur_frm`
✅ **Zero** ocorrências.

#### 3.2 Hex hardcoded
✅ **Zero** em `.js`/`.css` do app (cores do painel via CSS vars).

#### 3.3 Strings sem `__()`
⚠️ **`fee_agreement.js`:** mensagens de validação/gerar parcelas sem `__()` — corrigir no backlog UX.

✅ `legal_case.js`, `document_template.js`, painel modular: predominantemente com `__()`.

#### 3.4 APIs deprecadas
✅ **Zero** `$c_obj`, `add_fetch`.

#### 3.5 Lógica de negócio no JS
⚠️ **`fee_agreement.js`:** fluxo “Gerar Parcelas” com validações UX — espelhado em Python no controller; aceitável como UX-only.

✅ Sem cálculos financeiros críticos exclusivos de JS detectados.

---

### SEÇÃO 4 — hooks.py

#### 4.1 Fixtures
✅ Definido em `hooks.py`: Workspace, 2 Notifications, Custom Fields Event (`custom_source%`).

✅ **Não** exporta Server Script nem Client Script.

#### 4.2 Fixture JSONs
✅ `advocacia/fixtures/`: `workspace.json`, `notification.json`, `custom_field.json`.

#### 4.3 Anti-pattern fixtures
✅ **Ausentes** `server_script.json` e `client_script.json`.

#### 4.4 `doc_events`
✅ **Um handler por evento** por DocType (Legal Payment unificado em `processar_pagamento_on_update` + `on_trash` separado — OK).

#### 4.5 `scheduler_events`
✅ Daily (5 jobs) + weekly (`verificar_status_servicos`) — sem `commit()` nos módulos agendados.

---

### SEÇÃO 5 — Zero Lógica no Banco

#### 5.1 Server Scripts (`advocacia.local`)
✅ **Zero** Server Scripts no site.

#### 5.2 Client Scripts (`advocacia.local`)
✅ **Zero** Client Scripts no site.

---

### SEÇÃO 6 — Testes

#### 6.1 Cobertura
✅ **36 arquivos** `test_*.py` em `advocacia/advocacia/tests/` + 1 em doctype.

✅ **241 testes** executados com sucesso nesta auditoria.

Cobertura destacada: CRUD auxiliares, reports (6), `agent_api`, painel, financeiro, documentos, permissions, calendar sync.

#### 6.2 Stubs vazios (`pass`)
✅ **Zero** stubs `def test_*` + `pass` na suite central.

#### 6.3 Whitelisted vs testes
⚠️ Nem toda whitelist tem teste dedicado (ex.: `bulk_delete_pagamentos`, `get_events` calendário) — cobertura indireta via integração. Backlog: testes whitelist faltantes.

---

### SEÇÃO 7 — Workspace

#### 7.1 Content vs shortcuts
⚠️ **6 shortcuts** definidos em `shortcuts[]` sem bloco correspondente no `content` JSON:

- Comarca, Vara, Tribunal, Fase Processual, Tarefas, Documentos

✅ **12 shortcuts** referenciados no `content` estão corretamente definidos (Painel, Serviços, Pagamentos, Honorários, Prazos, Audiências, Clientes, 4 relatórios).

✅ Sidebar ↔ workspace links: **26 sidebar / 27 workspace links** — sincronização recente (labels PT).

---

### SEÇÃO 8 — Formatação e Versionamento

#### 8.1 Tabs vs spaces
✅ **Zero** defs Python com indentação de 4 espaços detectadas.

#### 8.2 Dead code / TODOs
✅ **Zero** `TODO`/`FIXME`/`HACK` em produção `.py`/`.js`.

---

### SEÇÃO 9 — Débito Específico Advocacia

#### 9.1 Painel modular
✅ **Modularizado** — maior arquivo `timeline.js` (426 linhas); total painel ~2.490 linhas JS + 2.130 CSS em 14 módulos; orquestrador `main.js`.

#### 9.2 Roles
✅ **Advocacia Manager** e **Advocacia User** presentes no site.

#### 9.3 Field descriptions
✅ **236/238 campos (99%)** com `description` no JSON — excelente cobertura.

---

### SEÇÃO 10 — Reinstall Test (Simulação)

| Balde | Conteúdo | Status |
| --- | --- | --- |
| **1. Código** | 24 DocTypes `custom:0`, page `painel`, 6 Script Reports, `agent_api.py` | ✅ |
| **2. Fixtures** | Workspace, Notifications, Custom Fields Event | ✅ |
| **3. Seed** | `after_install` + `after_migrate`: roles, permissions, sidebar, reports, translations, workspace, `ensure_office_settings` | ✅ |
| **Anti-pattern** | Server/Client Script em fixtures | ✅ Ausente |

**Recomendação pré-prod:** executar `bench --site NOVO install-app advocacia && migrate && run-tests` em VM limpa antes do go-live.

---

## Matriz Rápida — Bloqueadores Históricos vs Atual

| Check REGRAS | Jun/2026 |
| --- | --- |
| App instalável sem lógica no banco | ✅ |
| DocTypes `custom:0` | ✅ |
| Sem `commit()` em request/scheduler | ✅ |
| Whitelist com `has_permission` | ✅ |
| Zero Server Script no site | ✅ |
| Suite de testes verde | ✅ (241) |
| DocType names EN (v1.0.0) | ✅ |
| Office Settings completo (logo/banco/prazos) | ✅ |
| IA Fase 1 (`agent_api`) | ✅ |
| OpenAPI / MCP tools | ⚠️ Fase 2 |
| Workspace shortcuts órfãos | ⚠️ |
| N+1 `agent_api` | ⚠️ |
| i18n JS residual | ⚠️ |

---

## Plano de Migração (priorizado)

### Antes do go-live (recomendado, não bloqueante)

1. ⚠️ Smoke test em **site limpo** (`install-app` + migrate + 241 tests + abrir painel + gerar 1 docx).
2. ⚠️ Adicionar blocos `content` no workspace para os 6 shortcuts órfãos ou removê-los de `shortcuts[]`.
3. ⚠️ Definir `title_field: razao_social` em Office Settings (cosmético).

### Pós-deploy — curto prazo

4. ⚠️ Agregar contadores em `get_active_cases` (1 query vs 3×N `db.count`).
5. ⚠️ Internacionalizar `fee_agreement.js` (`__()` em msgprints).
6. ⚠️ Testes dedicados para whitelists sem cobertura (`bulk_delete_pagamentos`, eventos calendário).
7. ⚠️ Revisar `get_all` sem limit em schedulers quentes (`tasks.py`).

### Backlog v2

8. ⚠️ Fieldnames PT residuais (`titulo`, `nome`, `razao_social`) — só se política de idioma mudar.
9. ⚠️ Chart.js → `frappe.ui.Chart`.
10. ⚠️ Fase 2 IA: tools MCP + OpenAPI espelhando `agent_api.py`.
11. ⚠️ Migrar SQL residual do painel para `frappe.qb`.

---

## Comandos de Verificação Reprodutível

```bash
cd /home/frappe/frappe-bench/apps/advocacia
grep -r '"custom": 1' advocacia/advocacia/doctype/*/   # espera vazio
bench --site advocacia.local run-tests --app advocacia  # espera 241 OK
bench --site SITE_NOVO install-app advocacia && bench --site SITE_NOVO migrate
```

---

*Auditoria diagnóstica gerada em 2026-06-02. Nenhum arquivo de código foi alterado durante esta execução — apenas este relatório.*
