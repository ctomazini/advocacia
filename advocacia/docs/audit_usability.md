# Seção 3 — Verificação de Usabilidade

**App:** `advocacia` · **Data:** 2026-06-23 · **Versão:** 1.1.0 (pós-v1.1.0 hub + Office Settings)

---

## 3.1 Field descriptions (tooltips)

| Métrica | Valor |
|---|---:|
| Campos elegíveis (excl. Section/Column/Tab Break, HTML, Button) | 232 |
| Campos com `description` no JSON | 218 |
| Cobertura | **94%** (218/232) |
| Script de manutenção | `scripts/add_field_descriptions.py` |
| Aplicação | `bench execute advocacia.advocacia.scripts.add_field_descriptions.run` |

### DocTypes com descriptions completas (amostra)

| DocType | Campos descritos |
|---|---:|
| Fee Agreement | 37 |
| Legal Case | 22 |
| Service Record | 22 |
| Legal Payment | 18 |
| Hearing | 17 |
| Deadline | 16 |
| Client | 16 |
| Time Entry | 16 |

### Campos sem description (14 restantes)

Predominantemente: campos técnicos de sistema, flags internas de sync (`sincronizado_em`, `parcela_origem_id`) e breaks de layout em DocTypes menores. Prioridade baixa — backlog UX-06-018.

### Campos financeiros sensíveis

O script acrescenta sufixo *"Visível apenas para Advocacia Manager."* em campos com `permlevel: 1` — alinhado a `setup/permissions.py`.

---

## 3.2 Máscaras e UX de formulário

**Arquivo:** `public/js/masks.js` — incluído globalmente via `hooks.py`.

| Máscara | Padrão | DocTypes |
|---|---|---|
| CPF | `999.999.999-99` | Client |
| CNPJ | `99.999.999/9999-99` | Client, Office Settings |
| CNJ | `9999999-99.9999.9.99.9999` | Legal Case |
| Celular | `(99) 99999-9999` | Client Contact |
| Fixo | `(99) 9999-9999` | Client Contact |
| CEP | `99999-999` | Client Address |

**Regra:** JS só UX — validação real em `validators.py` no `validate()` do DocType.

### Outros JS globais

| Arquivo | Função |
|---|---|
| `list_nav.js` | Painel e Connections → lista com filtros (`frappe.set_route`) |
| `list_filters.js` | Barra de filtros responsiva (desktop visível / mobile ⇅) |
| `list_filters.css` | Layout da barra de filtros padrão |
| `case_hub.js` | Hub do Processo: abas, empty states, checklist, financeiro |
| `timer_global.js` | Timer de Time Entry no desk |

---

## 3.3 Workspace e sidebar

### Workspace `Advocacia`

- Fixture exportada em `fixtures/workspace.json`
- Sincronizada em `after_migrate` → `setup/workspace.ensure_advocacia_workspace`
- Seção **Comece Aqui** (Etapa 08): Clientes, Painel, Processos

### Sidebar (`setup/sidebar.py`)

| Seção | collapsible | Links |
|---|---|---|
| Dia a Dia | 1 | Painel, Prazos, Audiências, Tarefas, Comunicações |
| Gestão de Casos | 1 | Processos, Clientes, Documentos |
| Financeiro | 1 | Contratos, Recebimentos, Cobranças, Custas, Despesas |
| Relatórios | 1 | Script reports PT |
| Cadastros | 1 | Comarca, Vara, Tribunal, Fases, Modelos |

---

## 3.4 Painel do Escritório

- Page `/app/painel` — módulos em `public/js/painel/`
- Onboarding quando sem processos ativos (Etapa 08)
- Quick actions com chips `+ Cliente`, `+ Processo`, etc.
- Zona financeira restrita para Advocacia User

---

## 3.5 Hub do Processo (`Legal Case`)

| Recurso | Status pós-Etapa 09 |
|---------|---------------------|
| Checklist setup (honorários, prazo, audiência) | ✅ |
| Banner narrativo financeiro (Manager) | ✅ |
| Mensagem perfil User na aba Financeiro | ✅ |
| Empty states com título + hint + CTA | ✅ Etapa 09 |
| Pills de atalho por satélite | ✅ (plural por design — UX-06-009 backlog) |

---

## 3.6 Layout de formulários

Satélites transacionais usam **Column Break** para campos curtos (Link, Select, Date, Currency). Text Editor e tabelas permanecem full-width.

Oito formulários prioritários reorganizados na Etapa 07 (intros JS, tooltips financeiros, seções colapsáveis).

Detalhes: [audit_form_layout.md](./audit_form_layout.md).

---

## 3.7 List views

| DocType | `hide_name_column` | Indicador / formatter |
|---------|:------------------:|------------------------|
| Legal Case | ✅ | status |
| Legal Payment | ✅ | vencimento + status |
| Legal Task | ✅ | status + atraso (Etapa 09) |
| Deadline | ✅ | urgência / vencimento (Etapa 09) |
| Hearing | ✅ | data passada/futura (Etapa 09) |
| Fee Agreement | ✅ | — |
| + 7 outros | ✅ | variados |

### Mensagens de lista vazia (DocType `description`)

11 DocTypes transacionais com texto amigável na list view nativa (Etapa 09).

---

## 3.8 Demo data (dev)

| Comando | Função |
|---|---|
| `bench --site SITE seed-demo-advocacia` | Popula dados com `_DEMO_` |
| `bench --site SITE clear-demo-advocacia` | Remove por marcador |

**Produção:** não executar — módulo marcado dev-only.

---

## 3.9 Gaps de usabilidade (pós-Etapa 09)

| Gap | Severidade | Status |
|---|---|---|
| 14 campos sem description | 🟢 | Backlog UX-06-018 |
| Onboarding in-app | 🟢 | **Resolvido** Etapa 08 (painel + workspace) |
| Breadcrumb title em satélites | 🟡 | Backlog UX-06-004 |
| KPI total a receber no hub | 🟡 | Backlog UX-06-008 |
| Mobile desk | 🟡 | Painel responsivo parcial (CSS vars) |
| E2E CI | 🟢 | Playwright script manual; CI opcional |

---

## 3.10 Checklist UX pré-release

- [x] `bench build --app advocacia` após JS
- [x] `bench run-tests --app advocacia` verde (314)
- [x] Glossário Sprint 1A em painel e hub
- [x] Empty states hub com orientação
- [x] Intros financeiros em formulários prioritários
- [ ] Smoke: máscara CNJ em Legal Case novo (manual)
- [ ] Smoke: Connections em Processo abre lista filtrada (manual)
- [ ] Smoke: geração Word download (manual)

---

*Usabilidade pós-Etapa 09: descriptions 94%, onboarding, empty states hub, list indicators, forms reorganizados, projeto UX encerrado — ver `ux-final-executive-report.md`.*

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
