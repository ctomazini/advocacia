# Seção 3 — Verificação de Usabilidade

**App:** `advocacia` · **Data:** 2026-06-10 · **Versão:** 1.0.0

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

Predominantemente: campos técnicos de sistema, flags internas de sync (`sincronizado_em`, `parcela_origem_id`) e breaks de layout em DocTypes menores. Prioridade baixa — não bloqueiam deploy.

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

**Fallback:** se `jquery.inputmask` disponível (Frappe), usa inputmask nativo; senão `_bindInput` custom.

### Outros JS globais

| Arquivo | Função |
|---|---|
| `list_nav.js` | Painel e Connections → lista com filtros (`frappe.set_route`) |
| `list_filters.js` | Barra de filtros responsiva (desktop visível / mobile ⇅) |
| `list_filters.css` | Layout da barra de filtros padrão |
| `cliente_from_servico.js` | Preenche cliente ao selecionar serviço |
| `timer_global.js` | Timer de Time Entry no desk |

---

## 3.3 Workspace e sidebar

### Workspace `Advocacia`

- Fixture exportada em `fixtures/workspace.json`
- Sincronizada em `after_migrate` → `setup/workspace.ensure_advocacia_workspace`
- Cards e links alinhados ao fluxo operacional do escritório

### Sidebar (`setup/sidebar.py`)

| Seção | collapsible | Links |
|---|---|---|
| Dia a Dia | 1 | Painel, Prazos, Audiências, Legal Tasks, Comunicações |
| Gestão de Casos | 1 | Serviços, Clients, Horas, Atos, Custas |
| Financeiro | 1 | Legal Payments, Honorários, Despesas, Documentos, Kits |
| Relatórios | 1 (keep_closed) | 6 Script Reports |
| Cadastros | 1 (keep_closed) | Jurisdiction, Court Branch, Court, Fase, Escritório |

**Fix Frappe v16:** Section Breaks com filhos exigem `collapsible: 1` — sem isso o scroll do desk trava.

**Total links sidebar:** 26 entradas canônicas em `SIDEBAR_LINK_ORDER`.

---

## 3.4 List views

12 arquivos `*_list.js` em transacionais principais.

**Filtros padrão (`in_standard_filter`):** 17 DocTypes transacionais expõem Link/Select/Date na barra de filtros — ver `list_filters.js`.

| DocType | hide_name_column | Indicador status | Filtros rápidos |
|---|---|---|---|
| Legal Case | ✅ title | via status | ✅ |
| Client | ✅ nome + badge ID | 🟡 | ✅ |
| Legal Payment | ✅ | ✅ cores + Origem | ✅ |
| Fee Agreement | ✅ | ✅ | ✅ |
| Service Record | ✅ | ✅ | ✅ |
| Hearing | ✅ | ✅ | ✅ |
| Deadline | ✅ | ✅ | ✅ |
| Office Expense | ✅ | ✅ | ✅ |
| Court Cost | ✅ | ✅ | ✅ |
| Case Communication | ✅ | 🟡 | ✅ |
| Legal Task | ✅ | ✅ | ✅ |
| Time Entry | ✅ | 🟡 | ✅ |

**Gap:** cadastros auxiliares (Jurisdiction, Court Branch, Court) sem `*_list.js` custom — aceitável (poucos registros).

---

## 3.5 Títulos visíveis

| Padrão | Exemplo |
|---|---|
| Transacionais | `SERV-2026-0042 — Silva Advogados Ltda` |
| Client | `CLI-2026-0015 — João da Silva` (title_field = nome) |
| Cadastros | Nome do campo autoname |

`show_title_field_in_link: 1` nos transacionais — links e painel exibem descritor legível.

---

## 3.6 Fluxos operacionais

### Fluxo 1: Novo processo judicial

1. **Client** — CPF/CNPJ validado ✅  
2. **Jurisdiction / Court Branch / Court** — cadastro rígido ✅  
3. **Legal Case** — tipo Processo Judicial + CNJ ✅  
4. **Acordo de Honorarios** — parcelas + sync Legal Payment ✅  
5. **Painel** — KPIs e timeline ✅  

**Fricção:** 🟡 Orçamento de honorários complexo (modos Misto/Percentual) — descriptions ajudam.

### Fluxo 2: Prazo processual

1. **Deadline** — datas cronológicas validadas ✅  
2. **Event** — sync automático ✅  
3. **Notificação** — scheduler diário ✅  

### Fluxo 3: Cobrança de atos

1. **Service Record** — tabela Legal Act Item ✅  
2. **Gerar pagamento** — whitelist sync ✅  
3. **Legal Payment** — coluna Origem na list view ✅  

---

## 3.7 Demo data (dev)

| Comando | Função |
|---|---|
| `bench --site SITE seed-demo-advocacia` | Popula dados com `_DEMO_` |
| `bench --site SITE clear-demo-advocacia` | Remove por marcador |

**Produção:** não executar — módulo marcado dev-only.

---

## 3.8 Gaps de usabilidade

| Gap | Severidade | Ação sugerida |
|---|---|---|
| 14 campos sem description | 🟢 | Completar no próximo sprint UX |
| Onboarding in-app | 🟡 | Workspace intro ou vídeo |
| Mobile desk | 🟡 | Painel responsivo parcial (CSS vars) |
| E2E CI | 🟢 | Playwright script manual; CI opcional |

---

## 3.6 Layout de formulários

Satélites transacionais usam **Column Break** para campos curtos (Link, Select, Date, Currency). Text Editor e tabelas permanecem full-width.

Detalhes por DocType: [audit_form_layout.md](./audit_form_layout.md).

---

## 3.9 Checklist UX pré-release

- [ ] `bench build --app advocacia` após JS
- [ ] Smoke: máscara CNJ em Legal Case novo
- [ ] Smoke: tooltip em Acordo (campo honorários)
- [ ] Smoke: sidebar colapsa sem travar scroll
- [ ] Smoke: lista Legal Payment mostra coluna Origem
- [ ] Smoke: Connections em Serviço abre lista filtrada
- [ ] Smoke: filtros visíveis no desktop / ⇅ no mobile

---

*Usabilidade v1.0.0: descriptions 94%, filtros responsivos, connections filtradas, painel modular, forms 2 colunas.*
