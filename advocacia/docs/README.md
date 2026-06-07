# Documentação — App Advocacia

**Versão:** 1.0.0 · **Branch:** `frappe-v16` · **Atualizado:** 2026-06-02

---

## Por onde começar

| Público | Documento | Conteúdo |
| --- | --- | --- |
| Operador do escritório | [manual_usuario.md](./manual_usuario.md) | Fluxos, campos, painel, placeholders, listas |
| Desenvolvedor / deploy | [REGRAS_ADVOCACIA.md](../../REGRAS_ADVOCACIA.md) | Checklist normativo pré-deploy |
| Inventário técnico | [CODEBASE.md](../../CODEBASE.md) | DocTypes, hooks, API, árvore de arquivos |
| Instalação rápida | [README.md](../../README.md) | Bench, testes, seed-demo, E2E |

---

## Auditorias

Relatórios de conformidade. Consultar junto com [audit-deploy-ready.md](./audit-deploy-ready.md) antes de produção.

| Arquivo | Foco | Status jun/2026 |
| --- | --- | --- |
| [audit_code.md](./audit_code.md) | Python, whitelists, testes | Parcialmente desatualizado — ver CODEBASE |
| [audit_dashboard.md](./audit_dashboard.md) | Painel backend/frontend modular | ✅ painel modular + soft refresh |
| [audit_data_integrity.md](./audit_data_integrity.md) | CPF/CNPJ/CNJ, sync financeiro | ✅ |
| [audit_google_calendar.md](./audit_google_calendar.md) | Audiência/Prazo → Event → Google | ✅ |
| [audit_links.md](./audit_links.md) | Hub Legal Case, Connections | ✅ |
| [audit_usability.md](./audit_usability.md) | Máscaras, filtros, sidebar | ✅ labels PT jun/2026 |
| [audit_ai_readiness.md](./audit_ai_readiness.md) | `agent_api.py` + roadmap MCP | ✅ Fase 1 implementada |
| [audit-deploy-ready.md](./audit-deploy-ready.md) | Checklist pré-deploy consolidado | Referência histórica v0.7 |

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

### v1.0.0 — rename DocTypes EN + baseline produção

- 24 DocTypes renomeados PT→EN (Legal Case, Client, Office Settings, …)
- Painel com abas; `agent_api.py` inicial; tag `v1.0.0`

### pós v1.0.0 (jun/2026)

| Área | Mudança |
| --- | --- |
| **Office Settings** | Logo, dados bancários (banco/agência/conta/PIX), `default_notify_days` |
| **Documentos** | Referência completa de placeholders; logo inline docx; botão no Legal Case |
| **IA** | `get_active_cases`, `get_case_summary`, `get_court_costs_by_type`, `get_financial_overview` |
| **Painel** | Chaves EN alinhadas backend/frontend; handlers de KPI e links |
| **Relatórios** | 6 reports com KPIs, gráficos e formatação padronizada |
| **Sidebar / workspace** | Labels PT; traduções de DocType na UI |
| **Legal Payment** | Correção HTML na coluna Origem da list view |

---

## Testes

```bash
bench --site advocacia.local set-config allow_tests true
bench --site advocacia.local run-tests --app advocacia   # 241 testes (jun/2026)
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
