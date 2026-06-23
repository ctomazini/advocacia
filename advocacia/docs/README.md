# Documentação — App Advocacia

**Versão:** 1.1.0 · **Branch:** `ux/step-09-final-polish` · **Atualizado:** 2026-06-23

---

## Por onde começar

| Público | Documento | Conteúdo |
| --- | --- | --- |
| Operador do escritório | [manual_usuario.md](./manual_usuario.md) | Fluxos, campos, painel, placeholders, hub, documentos |
| Desenvolvedor / deploy | [REGRAS_ADVOCACIA.md](../../REGRAS_ADVOCACIA.md) | Checklist normativo pré-deploy |
| Cross-pollination engenharia | [CROSS_POLLINATION_ENGENHARIA.md](./CROSS_POLLINATION_ENGENHARIA.md) | Plano e prompt Agent para port de features |
| Documentos do processo | [case_documents.md](./case_documents.md) | Case Document, geração .docx, categorias |
| Navegação hub | [hub_navigation.md](./hub_navigation.md) | adv_case_nav.js, satélites, sessionStorage |
| Inventário técnico | [CODEBASE.md](../../CODEBASE.md) | DocTypes, hooks, API, árvore de arquivos |
| Instalação rápida | [README.md](../../README.md) | Bench, testes, seed-demo, E2E |

---

## Auditorias

Relatórios de conformidade. Consultar junto com [audit-deploy-ready.md](./audit-deploy-ready.md) antes de produção.

| Arquivo | Foco | Status jun/2026 |
| --- | --- | --- |
| [audit_code.md](./audit_code.md) | Python, whitelists, testes | ✅ 315 testes (jun/2026) |
| [audit_dashboard.md](./audit_dashboard.md) | Painel backend/frontend modular | ✅ P2 jun/2026 |
| [audit_data_integrity.md](./audit_data_integrity.md) | CPF/CNPJ/CNJ, sync financeiro | ✅ |
| [audit_google_calendar.md](./audit_google_calendar.md) | Audiência/Prazo → Event → Google | ✅ |
| [audit_links.md](./audit_links.md) | Hub Legal Case, Connections | ✅ |
| [audit_usability.md](./audit_usability.md) | Máscaras, filtros, sidebar, layout forms | ✅ jun/2026 |
| [audit_form_layout.md](./audit_form_layout.md) | Column Breaks e densidade de formulários | ✅ jun/2026 |
| [audit_ai_readiness.md](./audit_ai_readiness.md) | `agent_api.py` + roadmap MCP | ✅ Fase 1 implementada |
| [audit-deploy-ready.md](./audit-deploy-ready.md) | Checklist pré-deploy consolidado | Snapshot histórico — ver audits acima |

---

## Referência cruzada

| Arquivo | Conteúdo |
| --- | --- |
| [crosscheck_engenharia.md](./crosscheck_engenharia.md) | Snapshot advocacia ↔ engenharia |
| [e2e_playwright.md](./e2e_playwright.md) | Sessão E2E UI com Playwright |

---

## Scripts de manutenção

| Script | Comando |
| --- | --- |
| Field descriptions | `bench execute advocacia.advocacia.scripts.add_field_descriptions.run` |
| Manual do usuário | `bench execute advocacia.advocacia.scripts.generate_manual.main` |
| CODEBASE.md | `python scripts/generate_codebase.py` |
| Seed demo (dev) | `bench --site SITE seed-demo-advocacia` |
| Limpar demo (dev) | `bench --site SITE clear-demo-advocacia` |

---

## Entregas recentes

### v1.1.0 — UX final + hub + Office Settings (jun/2026)

| Área | Mudança |
| --- | --- |
| **UX Etapas 07–09** | Onboarding painel, checklist hub, glossário labels, list views com indicadores, empty states |
| **Hub Legal Case** | Pills em grid desktop (label em linha própria, sem clipping); carrossel mobile |
| **Documentos** | Download `.docx` via endpoint (sem diálogo Salvar como); labels Cobranças de Honorários / Individuais |
| **Office Settings** | CPF e RG da advogada principal + placeholders `escritorio_advogada_cpf` / `escritorio_advogada_rg` |
| **Validadores** | Correção ordem dígitos verificadores CNJ (Res. 65/2008) |
| **Painel** | Layout completo restaurado fora do modo onboarding |

Branch de entrega: `ux/step-09-final-polish` → merge em `main`.

### v1.0.0 — rename DocTypes EN + baseline produção

- 24 DocTypes renomeados PT→EN (Legal Case, Client, Office Settings, …)
- Painel com abas; `agent_api.py` inicial; tag `v1.0.0`

### jun/2026 — P1 Reports + P2 Painel

| Área | Mudança |
| --- | --- |
| **Relatórios P1** | `boot.py` (`adv_office`), `reports.css`, `reports_common.js`, print formats (9 Report + 3 DocType) |
| **Painel P2** | Backend/frontend modular; `main.js` orquestrador |
| **Form layout** | Column Breaks em 10 DocTypes satélites + auxiliares |
| **Office Settings** | Logo, dados bancários, `default_notify_days` |
| **Documentos** | Placeholders; logo inline docx |
| **IA** | `agent_api.py` — 4 endpoints read-only |
| **Documentos do processo** | Case Document, Document Category, hub documentos, geração → registro |
| **Navegação hub** | adv_case_nav.js — breadcrumb, voltar ao serviço, restaurar aba |
| **Sidebar / workspace** | Labels PT; traduções de DocType na UI |

---

## Testes

```bash
bench --site advocacia.local set-config allow_tests true
bench --site advocacia.local run-tests --app advocacia   # 315 testes (jun/2026)
```

E2E browser (opcional, fora da suite Frappe): ver [e2e_playwright.md](./e2e_playwright.md).

---

## API para agentes IA

Módulo `advocacia/advocacia/agent_api.py` — endpoints whitelisted read-only:

| Função | Permissão | Descrição |
| --- | --- | --- |
| `get_active_cases` | Legal Case read | Casos ativos + contadores |
| `get_case_summary` | Legal Case read | Resumo operacional; financeiro só Manager |
| `get_court_costs_by_type` | Manager | Custas agregadas por tipo |
| `get_financial_overview` | Manager | KPIs financeiros globais |

Detalhes: [audit_ai_readiness.md](./audit_ai_readiness.md).

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
