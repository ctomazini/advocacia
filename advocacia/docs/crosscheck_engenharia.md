# Cross-audit: advocacia ↔ engenharia

> **Atualização:** 2026-06-10 — P1 Reports + P2 Painel modular.

## Paridade alcançada

| Área | Advocacia | Engenharia |
| --- | --- | --- |
| Fixtures Role + Kanban | ✅ `role.json`, `Advocacia Tarefas` | ✅ |
| Notification fixtures | ✅ 4 templates | ✅ 4 templates |
| `test_csv_import.py` | ✅ | ✅ |
| `test_whitelist.py` | ✅ | ✅ |
| Scheduler tarefas atrasadas | ✅ `notificar_tarefas_atrasadas` | ✅ |
| DocType dashboards | ✅ 11 connections | ✅ 12 (domínio obra) |
| `agent_api` batch counts | ✅ `get_active_cases` | ✅ `get_active_projects` |
| Painel modular backend | ✅ `painel/` (9 módulos) | ✅ `dashboard/` (12 módulos) |
| Painel modular frontend | ✅ `public/js/painel/` (14 arquivos, `main.js`) | ✅ `public/js/dashboard/` (13 arquivos) |
| Payload painel | ✅ `saude_operacional`, `atencao`, `proximo_evento`, `active_cases` | ✅ equivalentes |
| Reports boot + print | ✅ `boot.py`, print formats Report | ✅ |
| `list_nav.js` | ✅ | ✅ |
| Lazy-load painel | ✅ `PAINEL_ASSETS` na Page | ✅ `ENG_DASH_ASSETS` na Page |
| `report_visuals.py` + formatters | ✅ 6 reports | ✅ 5 reports |
| `importable_doctypes` | ✅ 5 DocTypes | ✅ |
| Print formats + seed | ✅ | ✅ |
| E2E npm | ✅ `e2e/` | ✅ |
| Ruff + `.cursorrules` + `CODEBASE.md` | ✅ | ✅ |

## Divergências intencionais (manter)

| Item | Motivo |
| --- | --- |
| DocTypes PT vs EN | advocacia brownfield; engenharia greenfield |
| Hub `Legal Case` vs `Construction Project` | domínios distintos |
| KPIs e tiles do painel | jurídico vs obra (protocolos, custos de obra, comissões) |
| `agent_api` endpoints | superfícies de domínio diferentes |
| Office Expense sem Link `legal_case` | sem dashboard hub-linked (by design) |
| Nomenclatura backend painel PT vs EN | `financeiro`/`prazos` vs `financial`/`deadlines` |
| CSS painel em `page/painel/` vs `public/css/dashboard.css` | padrões distintos, ambos funcionais |
| Chart.js no painel advocacia | backlog: migrar para `frappe.ui.Chart` |

## Backlog restante

| Item | Prioridade |
| --- | --- |
| Chart.js → `frappe.ui.Chart` no painel | baixa |
| Migrar SQL do painel para `frappe.qb` | baixa |
| Fieldnames EN/PT em auxiliares (`city`, `phase_name`) | cosmético v2 |

## Verificação

```bash
cd /home/frappe/frappe-bench
bench --site advocacia.local migrate
bench build --app advocacia
bench --site advocacia.local run-tests --app advocacia
```

Smoke manual: `/app/painel` (Saúde, Atenção, Agenda, Financeiro Manager), Kanban **Advocacia Tarefas**, import CSV em Client/Legal Case.

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
