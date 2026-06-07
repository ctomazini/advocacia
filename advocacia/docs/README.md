# Documentação — App Advocacia

**Versão:** 0.7.0 · **Branch:** `frappe-v16` · **Atualizado:** 2026-06-07

---

## Por onde começar

| Público | Documento | Conteúdo |
| --- | --- | --- |
| Operador do escritório | [manual_usuario.md](./manual_usuario.md) | Fluxos, campos, painel, listas |
| Desenvolvedor / deploy | [REGRAS_ADVOCACIA.md](../../REGRAS_ADVOCACIA.md) | Checklist normativo pré-deploy |
| Inventário técnico | [CODEBASE.md](../../CODEBASE.md) | DocTypes, hooks, API, árvore de arquivos |
| Instalação rápida | [README.md](../../README.md) | Bench, testes, seed-demo, E2E |

---

## Auditorias (v0.7.0)

Relatórios de conformidade gerados na fase 2. Atualizar quando o código mudar.

| Arquivo | Foco |
| --- | --- |
| [audit_code.md](./audit_code.md) | Python, whitelists, 230 testes, disciplinas |
| [audit_dashboard.md](./audit_dashboard.md) | Painel backend/frontend modular, soft refresh |
| [audit_data_integrity.md](./audit_data_integrity.md) | CPF/CNPJ/CNJ, sync financeiro |
| [audit_google_calendar.md](./audit_google_calendar.md) | Audiência/Prazo → Event → Google |
| [audit_links.md](./audit_links.md) | Hub Servico, Connections, navegação filtrada |
| [audit_usability.md](./audit_usability.md) | Máscaras, filtros de lista, sidebar, tooltips |
| [audit_ai_readiness.md](./audit_ai_readiness.md) | Roadmap `agent_api.py` (pós-deploy) |

---

## Referência cruzada

| Arquivo | Conteúdo |
| --- | --- |
| [crosscheck_engenharia.md](./crosscheck_engenharia.md) | Snapshot advocacia ↔ engenharia (referência) |
| [e2e_playwright.md](./e2e_playwright.md) | Sessão E2E UI com Playwright |

---

## Scripts de manutenção

| Script | Comando |
| --- | --- |
| Field descriptions | `bench execute advocacia.advocacia.scripts.add_field_descriptions.run` |
| Manual do usuário | `bench execute advocacia.advocacia.scripts.generate_manual.run` |
| Seed demo (dev) | `bench --site SITE seed-demo-advocacia` |
| Limpar demo (dev) | `bench --site SITE clear-demo-advocacia` |

---

## Entregas recentes (jun/2026)

| Área | Mudança | Onde documentado |
| --- | --- | --- |
| Filtros de lista | `in_standard_filter` em 17 DocTypes; barra responsiva desktop/mobile | audit_usability, manual |
| Connections | Clique abre lista já filtrada pelo documento pai | audit_links, list_nav.js |
| Painel | Soft refresh (período e limites sem reload total) | audit_dashboard |
| E2E UI | Script Playwright com marcador `_PW_E2E_` | e2e_playwright.md |

---

## Testes

```bash
bench --site advocacia.local set-config allow_tests true
bench --site advocacia.local run-tests --app advocacia   # 230 testes (jun/2026)
```

E2E browser (opcional, fora da suite Frappe): ver [e2e_playwright.md](./e2e_playwright.md).
