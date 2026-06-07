# REGRAS_ADVOCACIA.md

**App:** `advocacia` · **Frappe v16** (sem ERPNext) · **Versão:** 0.7.0 · **Data:** 2026-06-07  
**Branch:** `frappe-v16` · **Objetivo:** checklist operacional fechado para deploy.

> `ENGENHARIA_STANDARDS.md` governa o app **engenharia**, não este repositório.

---

## 1. Identidade

| Decisão | Regra |
| --- | --- |
| DocTypes | 24, todos `custom: 0`, módulo `Advocacia` |
| Nomes DocType | **Português congelado** — não renomear |
| Fieldnames | `snake_case`; labels UI em português |
| Hub | `Servico` — 9 satélites com campo `servico` |
| Testes | 230 (`run-tests --app advocacia`) |

---

## 2. Dados e validações

**Links obrigatórios (nunca texto livre):** Comarca, Vara, Tribunal, Fase Processual, Cliente, Servico.

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
| Backend | `advocacia/painel/` — orquestrador `get()` |
| Facade | Único `xcall`: `painel_api.get_painel_data` |
| Frontend | `public/js/painel/` (7 módulos) + shell `page/painel/painel.js` |
| Permissão | `Servico` read na entrada |
| Financeiro | `strip_financial_payload` para **Advocacia User** |
| Commit | Nunca no `get()` |
| Soft refresh | Período e `list_limits` recarregam payload sem reload da page |

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

**Sync** (`financeiro.py`): Acordo → Pagamento idempotente via `parcela_origem_id`; flag `in_pagamento_sync`; `manual_override` respeitado; um handler `on_update` por DocType.

**Calendar** (`calendar_sync.py`): Audiencia + Controle de Prazos → Event; `custom_source_*`; `ignore_permissions` comentado.

**Roles:** Advocacia User (operacional, sem financeiro no painel) · Advocacia Manager (full).

Setup: `setup/roles.py` + `setup/permissions.py` no `after_migrate`.

---

## 6. Hooks resumido

**Fixtures:** Workspace Advocacia, Notifications, Custom Fields em Event.

**Scheduler:** 5 daily + 1 weekly (parcelas, despesas, prazos, audiências, status serviços).

**`after_migrate`:** roles → permissions → install → translations → sidebar → reports → workspace.

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

Script manual: `advocacia/advocacia/tests/e2e/playwright_flow.py`  
Marcador: `_PW_E2E_` — cleanup automático.  
Documentação: `advocacia/docs/e2e_playwright.md`

```bash
export ADVOCACIA_E2E_PWD='...'
bench --site advocacia.local serve --port 8000 --noreload
python advocacia/advocacia/tests/e2e/playwright_flow.py
```

---

## 8. Checklist pré-commit / pré-deploy

- [ ] DocTypes PT — sem renomeação breaking
- [ ] `custom: 0`; validadores BR no controller
- [ ] Sem `commit()` fora de `setup/`/`patches/`/`seed_demo`
- [ ] Whitelist: `has_permission` + type hints
- [ ] Queries com limit; sem N+1
- [ ] `doc_events`: um handler por evento
- [ ] `run-tests` verde (230)
- [ ] Sem segredos/dados reais no diff
- [ ] Conventional Commit (`feat:`, `fix:`, `refactor:`, `chore:`)
- [ ] Snapshot Proxmox antes de mudança destrutiva em produção

---

## 9. Documentação de auditoria (v0.7.0)

| Arquivo | Conteúdo |
| --- | --- |
| `advocacia/docs/README.md` | Índice da documentação |
| `advocacia/docs/e2e_playwright.md` | E2E UI Playwright |
| `advocacia/docs/audit_code.md` | Código, 230 testes, whitelists |
| `advocacia/docs/audit_dashboard.md` | Painel modular backend/frontend |
| `advocacia/docs/audit_data_integrity.md` | CPF/CNPJ/CNJ/telefone, sync |
| `advocacia/docs/audit_google_calendar.md` | Event + Google |
| `advocacia/docs/audit_links.md` | Hub Servico e satélites |
| `advocacia/docs/audit_usability.md` | Máscaras, 218/232 descriptions |
| `advocacia/docs/audit_ai_readiness.md` | `agent_api.py` pós-deploy |
| `CODEBASE.md` | Inventário técnico |

---

## 10. Proibido

- Renomear DocTypes para inglês
- Usar `ENGENHARIA_STANDARDS.md` como norma deste app
- `commit()` em hooks de sync ou API
- Texto livre para cadastros rígidos (comarca/vara/tribunal)
- `seed-demo` em produção
- Alterar core Frappe

---

*Norma do app advocacia. Atualizar neste arquivo no mesmo PR que mudar o padrão.*
