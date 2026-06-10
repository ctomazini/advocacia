# Seção 4 — Verificação do Painel (Dashboard)

**Page:** `painel` (`advocacia/advocacia/page/painel/`)  
**Backend:** `advocacia/painel/` · **Facade:** `painel_api.py`  
**Frontend modular:** `public/js/painel/` · **Data:** 2026-06-09 · **Versão app:** 0.7.0

---

## 4.1 Arquitetura

### Camadas

```
page/painel/painel.js (shell + PAINEL_ASSETS)
    └── frappe.require → public/js/painel/
            ├── utils.js       — caps, formatação, CSS vars, list limits
            ├── hero.js        — cabeçalho, período, ações rápidas
            ├── kpis.js        — KPIs financeiros (zona financeira)
            ├── saude.js       — saúde operacional (compact)
            ├── atencao.js     — tiles de atenção
            ├── agenda.js      — próximo evento
            ├── timeline.js    — agenda unificada, comunicações
            ├── financeiro.js  — composição, duos, parcelas, despesas, custas
            ├── operational.js — processos ativos
            ├── refresh.js     — skeleton, soft refresh, patch seções
            ├── sections.js    — HTML parcial para patch
            ├── handlers.js    — filtros, rotas, marcar parcela
            ├── main.js        — load() + render() (orquestrador)
            └── index.js       — init() bootstrap da Page

xcall → advocacia.advocacia.painel_api.get_painel_data
            └── painel/__init__.py::get()
                    ├── kpis.py
                    ├── financeiro.py
                    ├── prazos.py
                    ├── timeline.py
                    ├── agenda.py
                    ├── atencao.py
                    ├── saude.py
                    └── operational.py
```

**Evolução:** monolito `painel.js` (~4.100 linhas, jun/2026) → módulos JS + backend modular. P2 (jun/2026): `main.js` extraído de `index.js`; `audiencias.js` removido (código morto — funções migradas para `atencao.js` / `agenda.js`).

**Assets:** carregados via `frappe.require(PAINEL_ASSETS)` na Page — **não** em `hooks.py` global.

**CSS:** `page/painel/painel.css` (~2.130 linhas), co-localizado com a Page.

### Módulos backend e linhas

| Módulo | Linhas | Responsabilidade |
|---|---:|---|
| `__init__.py` | 129 | Orquestrador `get()`, monta payload estável |
| `_helpers.py` | 145 | Caps, normalização, lookups batch, `strip_financial_payload` |
| `kpis.py` | 184 | KPIs agregados, `summary` |
| `financeiro.py` | 274 | Parcelas, despesas, custas, fluxo, `marcar_parcela` |
| `prazos.py` | 177 | Audiências, prazos, centro de atenção (interno) |
| `timeline.py` | 249 | Legal Tasks, comunicações, horas, timeline |
| `agenda.py` | 45 | `proximo_evento` |
| `atencao.py` | 115 | Tiles de atenção |
| `saude.py` | 55 | Saúde operacional |
| `operational.py` | 107 | Processos ativos enriquecidos |
| `painel_api.py` | 30 | Facade whitelisted (único path de `xcall`) |

**Total backend painel:** ~1.480 linhas.

### Módulos frontend e linhas

| Módulo | Linhas | Responsabilidade |
|---|---:|---|
| `utils.js` | 294 | Helpers, limites 5/10/15, polish chrome |
| `hero.js` | 207 | Header, filtro período (1/7/15/30 dias), ações rápidas |
| `kpis.js` | 96 | KPIs financeiros (zona financeira) |
| `saude.js` | 75 | Saúde operacional |
| `atencao.js` | 105 | Tiles de atenção |
| `agenda.js` | 97 | Próximo evento |
| `timeline.js` | 427 | Timeline, comunicações |
| `financeiro.js` | 379 | Zona financeira (Manager only) |
| `operational.js` | 81 | Processos ativos |
| `refresh.js` | 119 | Soft refresh, skeleton, patch |
| `sections.js` | 121 | HTML parcial por seção |
| `handlers.js` | 318 | Eventos, rotas, marcar parcela |
| `main.js` | 141 | `load()` + `render()` |
| `index.js` | 31 | `init()` bootstrap |
| `painel.js` (page) | 33 | Shell Frappe Page + ordem de assets |

**Total frontend painel:** ~2.490 linhas (+ `painel.css`).

---

## 4.2 Contrato do orquestrador

### Entrada (`get()`)

| Parâmetro | Default | Cap |
|---|---|---|
| `limit_start` | 0 | — |
| `limit_page_length` | 20 | max 100 |
| `periodo_dias` | 7 | 1, 7, 15 ou 30 |
| `list_limits` | por chave | 5, 10 ou 15 por seção |

### Chaves do payload (estáveis — front depende)

| Chave | Origem | Manager | User |
|---|---|---|---|
| `periodo_dias`, `list_limits`, `list_meta`, `is_manager` | `__init__` | ✅ | ✅ |
| `kpis` | kpis.py | completo | sem chaves financeiras |
| `summary` | kpis.py | completo | sem valores financeiros |
| `financeiro` | financeiro.py | ✅ | ❌ omitido (`strip_financial_payload`) |
| `saude_operacional` | saude.py | ✅ | ❌ omitido |
| `atencao` | atencao.py | ✅ | ✅ |
| `proximo_evento` | agenda.py | ✅ | ✅ |
| `timeline` | timeline.py + prazos.py | ✅ | ✅ |
| `active_cases` | operational.py | ✅ | ✅ |
| `fee_installments` | financeiro.py | ✅ | ❌ |
| `despesas_pendentes`, `total_despesas_mes` | financeiro.py | ✅ | ❌ |
| `custas_pendentes_repasse`, `total_custas_mes` | financeiro.py | ✅ | ❌ |
| `comunicacoes_pendentes`, `ultimas_comunicacoes` | timeline.py | ✅ | ✅* |
| `horas_semana`, `horas_periodo` | timeline.py | ✅ | ✅* |

\*Comunicações e horas exigem read no DocType — retorna lista vazia se negado.

### Permissões

```python
# painel_api.py
frappe.has_permission("Legal Case", "read", throw=True)

# painel/__init__.py
if not frappe.has_permission("Legal Case", "read"):
    frappe.throw(...)

# _helpers.strip_financial_payload
user_is_advocacia_manager() → Advocacia Manager
```

**Zero `frappe.db.commit()`** no `get()` — ✅.

---

## 4.3 Queries principais

| Origem | DocType(s) | Limit |
|---|---|---|
| KPIs | Legal Case, Client, Legal Payment, Hearing, Deadline | `LIST_LIMIT_MAX=100` |
| Financeiro | Legal Payment, Office Expense, Court Cost | 100 + list_cap |
| Prazos | Hearing, Deadline | 100 |
| Timeline | Legal Task, Case Communication, Time Entry | 100 |

**N+1:** evitado via `_servico_lookup`, `_cliente_nome_lookup`, `_user_nome_lookup` — uma query em lote por lookup.

**Nomes legíveis:** satélites exibem `title` do Legal Case/Client, não IDs crus.

---

## 4.4 Frontend — comportamento por role

| Componente | Manager | User |
|---|---|---|
| Hero + filtro período | ✅ | ✅ |
| KPIs operacionais (clientes, casos, audiências) | ✅ | ✅ |
| KPIs financeiros (honorários, taxa recebimento) | ✅ | Ocultos (backend + JS) |
| Tiles de atenção + próximo evento | ✅ | ✅ |
| Timeline / agenda | ✅ | ✅ |
| Processos ativos | ✅ | ✅ |
| Comunicações pendentes | ✅ | ✅ |
| Zona financeira (saúde, KPIs, composição, listas) | ✅ | Removida do DOM |
| Marcar parcela recebida | ✅ | Botão ausente |
| Navegação `list_nav.goto` | ✅ | ✅ |

**Cores:** charts e cards usam CSS variables Frappe — sem hex hardcoded no JS de produção.

**Refresh:** botão ↺ Atualizar; limites 5/10/15 e filtro de período recarregam payload via xcall **sem reload total** da page (soft refresh).

---

## 4.5 Facade whitelisted

```python
# advocacia.advocacia.painel_api
get_painel_data(...) -> dict      # type hints ✅
marcar_parcela_recebida(name) -> dict
```

Front chama:
```javascript
frappe.xcall("advocacia.advocacia.painel_api.get_painel_data", {...})
```

**Nunca** chamar submódulos `painel.kpis` etc. diretamente do client.

---

## 4.6 Inconsistências conhecidas

| Item | Severidade | Nota |
|---|---|---|
| `limit_page_length` no backend | 🟡 | Migrar para `limit` (v17) |
| Nomenclatura PT backend (`financeiro`, `prazos`) vs EN eng (`financial`, `deadlines`) | 🟢 | Intencional — brownfield advocacia |
| CSS em `page/painel/` vs eng `public/css/dashboard.css` | 🟢 | Padrões diferentes, ambos funcionais |
| E2E browser automatizado | 🟡 | `test_painel_api.py` + `test_painel_modulos.py` + Playwright manual |

---

## 4.7 Checklist pós-mudança painel

- [ ] `bench build --app advocacia` após editar `public/js/painel/`
- [ ] `bench --site advocacia.local clear-cache`
- [ ] `bench --site advocacia.local run-tests --app advocacia` — testes painel verdes
- [ ] Smoke manual: soft refresh ao mudar período/limites
- [ ] Smoke manual: User sem financeiro · Manager com gráfico

---

*Painel modular desde v0.7.0. Referência estrutural: `engenharia/dashboard/` + `engenharia/public/js/dashboard/`.*
