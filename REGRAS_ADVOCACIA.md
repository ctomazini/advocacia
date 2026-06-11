# REGRAS_ADVOCACIA.md

**App:** `advocacia` · **Frappe v16** (sem ERPNext) · **Versão:** 0.7.1 · **Data:** 2026-06-11  
**Branch:** `main` · **Objetivo:** checklist operacional fechado para deploy.

> **Nomenclatura (desde v1.0.0, jun/2026):** DocTypes em **inglês** Title Case (`Legal Case`, `Client`, …); **labels** e mensagens UI em **português**; **`fieldname`** em `snake_case` **majoritariamente inglês** (patches `rename_fields_pt_en.py` — resíduos PT cosméticos documentados em auditorias). **Não** renomear DocTypes sem patch + migrate + testes.

> `ENGENHARIA_STANDARDS.md` governa o app **engenharia**, não este repositório.

---

## 1. Identidade

| Decisão | Regra |
| --- | --- |
| DocTypes | 24, todos `custom: 0`, módulo `Advocacia` |
| Nomes DocType | **Inglês** Title Case singular — definitivos desde **v1.0.0** (ex.: `Legal Case`, `Fee Agreement`) |
| Fieldnames | `snake_case`, **preferencialmente inglês**; labels UI em português |
| Hub | `Legal Case` — satélites com link `legal_case` (ou equivalente documentado) |
| Testes | `bench --site advocacia.local run-tests --app advocacia` (ver `CODEBASE.md` / auditorias para contagem vigente) |

---

## 2. Dados e validações

**Links obrigatórios (nunca texto livre):** Jurisdiction, Court Branch, Court, Case Phase, Client, Legal Case.

**Armazenamento:** CPF/CNPJ/CNJ/telefone → só dígitos; e-mail → `.lower()`.

**Validadores** (`validators.py`): CPF/CNPJ (Receita Federal), CNJ (Módulo 97), telefone (ANATEL), e-mail. Aplicar no `validate()` do DocType — JS (`masks.js`) é só UX.

**Títulos** (`titulos.py`): `{ID} — {descritor}`; `validate` + `after_insert`; `show_title_field_in_link: 1`.

---

## 3. Disciplinas não negociáveis

| # | Regra |
| --- | --- |
| 1 | Zero `frappe.db.commit()` em whitelisted, `doc_events`, scheduler — só `setup/`, `patches/`, `seed_demo.py` |
| 2 | `ignore_permissions=True` só com comentário (`financeiro.py`, `calendar_sync.py`, `documentos.py`, `setup/*`) |
| 3 | Whitelisted: `has_permission(..., throw=True)`; type hints em endpoints novos |
| 4 | Zero N+1 — batch lookups (`painel/_helpers.py`) |
| 5 | Queries com `limit_page_length` ou cap |
| 6 | Um handler por `(DocType, evento)` em `doc_events` |
| 7 | Scheduler: falha em um item não aborta o lote |
| 8 | Sem `eval`/`exec`; sem `except Exception: pass` |
| 9 | JS: sem `cur_frm`, `add_fetch`, `$c_obj`; charts com CSS vars |
| 10 | Demo: `DEMO_MARKER = "_DEMO_"` — **proibido em produção** |
| 11 | Listas: `in_standard_filter` em campos Link/Select/Date repetitivos |
| 12 | Connections: navegação filtrada via `list_nav.js`, nunca lista genérica |

---

## 4. Painel

| Item | Regra |
| --- | --- |
| Backend | `advocacia/painel/` — orquestrador `get()` (9 módulos: kpis, financeiro, prazos, timeline, agenda, atencao, saude, operational, _helpers) |
| Facade | Único `xcall`: `painel_api.get_painel_data` |
| Frontend | `public/js/painel/` (14 arquivos) — carregado **somente** na Page via `frappe.require(PAINEL_ASSETS)` em `page/painel/painel.js` |
| Orquestrador JS | `main.js` (`load` + `render`); `index.js` (`init`); infra: `refresh.js`, `sections.js`, `handlers.js` |
| CSS | `page/painel/painel.css` (~2.130 linhas) — co-localizado com a Page |
| Permissão | `Legal Case` read na entrada |
| Financeiro | `strip_financial_payload` para **Advocacia User** |
| Commit | Nunca no `get()` |
| Soft refresh | Período e `list_limits` recarregam payload sem reload da page |

### Layout de formulários (satélites)

| Item | Regra |
| --- | --- |
| Escopo | Todos os DocTypes **exceto** `Legal Case` (hub com abas) |
| Campos curtos | Usar **Column Break** na mesma seção (padrão `Deadline` / `Hearing`) |
| Text Editor / Table | Largura total — sem coluna ao lado |
| Referência | `advocacia/docs/audit_form_layout.md` |

---

## 4.1 Listas e filtros

| Item | Regra |
| --- | --- |
| Filtros padrão | `in_standard_filter: 1` em Link/Select/Date dos transacionais |
| Desktop | Barra de filtros sempre visível (`list_filters.css`) |
| Mobile | Filtros no botão nativo ⇅ (`list_filters.js`) |
| Connections | Clique em count/link → `advocacia.list_nav.goto` ou `open_connection_list` |
| Painel → lista | `frappe.set_route("List", doctype, filterObject)` |

---

## 5. Financeiro e calendar

**Sync** (`financeiro.py`): Acordo → Legal Payment idempotente via `parcela_origem_id`; flag `in_pagamento_sync`; `manual_override` respeitado; um handler `on_update` por DocType.

**Calendar** (`calendar_sync.py`): Hearing + Deadline → Event; `custom_source_*`; `ignore_permissions` comentado.

**Roles:** Advocacia User (operacional, sem financeiro no painel) · Advocacia Manager (full).

Setup: `setup/roles.py` + `setup/permissions.py` no `after_migrate`.

---

## 6. Hooks resumido

**Fixtures:** Workspace Advocacia, Notifications, Custom Fields em Event.

**Scheduler:** 5 daily + 1 weekly (parcelas, despesas, prazos, audiências, status serviços).

**`after_migrate`:** roles → permissions → install → translations → sidebar → reports → workspace.

---

## 6.1 Script Reports

| Item | Regra |
| --- | --- |
| Cores / charts | `report_visuals.py` — sem hex inline nos `.py` |
| KPIs | `currency_summary`, `int_summary`, `percent_summary` |
| Grid | `formatter()` nos `.js` — classes Frappe (`indicator-pill`, `text-danger`, `bold`) |

---

## 6.2 Print Formats e seed produção

| Item | Regra |
| --- | --- |
| HTML | `advocacia/print_formats/*.html` (Jinja) |
| Sync | `setup/print_formats.ensure_advocacia_print_formats` no `after_migrate` |
| Seed | `setup/seed.ensure_seed_data` — Case Phase universal, idempotente |
| CSV import | `importable_doctypes` em `hooks.py` + `allow_import: 1` nos DocTypes listados |

---

## 6.3 Doctype dashboards

| Item | Regra |
| --- | --- |
| Arquivo | `{doctype_snake}_dashboard.py` com `get_data()` |
| Links | `internal_links` + `non_standard_fieldnames` quando o campo não segue convenção Frappe |
| JSON | `links[]` no DocType hub/satélites — sem duplicar o mesmo DocType em grupos diferentes |

---

## 7. Comandos bench

```bash
bench --site advocacia.local migrate
bench --site advocacia.local clear-cache    # após JS de DocType
bench build --app advocacia                 # após public/js/ ou public/css/
bench --site advocacia.local run-tests --app advocacia
bench export-fixtures --app advocacia       # antes de commit
bench --site advocacia.local seed-demo-advocacia   # DEV ONLY
bench --site advocacia.local clear-demo-advocacia  # DEV ONLY
bench restart
```

---

## 7.1 E2E Playwright (opcional)

Pacote npm: `e2e/` (`npm test` após `npm install`).  
Variáveis: `E2E_BASE_URL`, `E2E_SITE_HOST`, `E2E_USER`, `E2E_PASS`.  
Marcador: `PLAYWRIGHT_<run_id>`.  
Wrapper Python legado: `tests/e2e/playwright_flow.py` (preferir npm).

```bash
cd e2e && npm install && npm run install:browsers
export E2E_PASS='...'
bench --site advocacia.local serve --port 8000 --noreload
npm test
```

---

## 8. Checklist pré-commit / pré-deploy

- [ ] DocTypes PT — sem renomeação breaking
- [ ] `custom: 0`; validadores BR no controller
- [ ] Sem `commit()` fora de `setup/`/`patches/`/`seed_demo`
- [ ] Whitelist: `has_permission` + type hints
- [ ] Queries com limit; sem N+1
- [ ] `doc_events`: um handler por evento
- [ ] `run-tests` verde (283+)
- [ ] Sem segredos/dados reais no diff
- [ ] Conventional Commit (`feat:`, `fix:`, `refactor:`, `chore:`)
- [ ] Snapshot Proxmox antes de mudança destrutiva em produção

---

## 9. Documentação de auditoria (v1.0.0)

| Arquivo | Conteúdo |
| --- | --- |
| `advocacia/docs/README.md` | Índice da documentação |
| `advocacia/docs/e2e_playwright.md` | E2E UI Playwright |
| `advocacia/docs/audit_code.md` | Código, 283 testes, whitelists |
| `advocacia/docs/audit_dashboard.md` | Painel modular backend/frontend |
| `advocacia/docs/audit_form_layout.md` | Layout 2 colunas nos formulários |
| `advocacia/docs/audit_data_integrity.md` | CPF/CNPJ/CNJ/telefone, sync |
| `advocacia/docs/audit_google_calendar.md` | Event + Google |
| `advocacia/docs/audit_links.md` | Hub Legal Case e satélites |
| `advocacia/docs/audit_usability.md` | Máscaras, 218/232 descriptions |
| `advocacia/docs/audit_ai_readiness.md` | `agent_api.py` Fase 1 (implementado) |
| `CODEBASE.md` | Inventário técnico |

---

## 10. Proibido

- Renomear DocTypes ou `fieldname` **sem** patch idempotente + `migrate` + testes verdes
- Usar `ENGENHARIA_STANDARDS.md` como norma deste app
- `commit()` em hooks de sync ou API
- Texto livre para cadastros rígidos (comarca/vara/tribunal)
- `seed-demo` em produção
- Alterar core Frappe

---

*Norma do app advocacia. Atualizar neste arquivo no mesmo PR que mudar o padrão.*
