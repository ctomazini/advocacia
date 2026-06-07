# Seção 4 — Verificação do Painel (Dashboard)

**Page:** `painel` (`advocacia/advocacia/page/painel/`)  
**Backend:** `advocacia/painel/` · **Facade:** `painel_api.py`  
**Frontend modular:** `public/js/painel/` · **Data:** 2026-06-07 · **Versão app:** 0.7.0

---

## 4.1 Arquitetura

### Camadas

```
painel.js (shell, 13 linhas)
    └── advocacia.painel.init()  →  public/js/painel/index.js
            ├── utils.js      — caps, formatação, CSS vars, list limits
            ├── hero.js       — cabeçalho, período, ações rápidas
            ├── kpis.js       — tiles KPI + resumo
            ├── audiencias.js — alertas, centro de atenção
            ├── timeline.js   — agenda unificada
            └── financeiro.js — parcelas, despesas, custas, gráficos

xcall → advocacia.advocacia.painel_api.get_painel_data
            └── painel/__init__.py::get()
                    ├── kpis.py
                    ├── financeiro.py
                    ├── prazos.py
                    └── timeline.py
```

**Evolução:** o monolito `painel.js` (~4.100 linhas, jun/2026) foi dividido em 7 módulos JS (~2.480 linhas) + shell mínimo. Backend já era modular desde a auditoria anterior.

### Módulos backend e linhas

| Módulo | Linhas | Responsabilidade |
|---|---:|---|
| `__init__.py` | 113 | Orquestrador `get()`, monta payload estável |
| `_helpers.py` | 143 | Caps, normalização, lookups batch, `strip_financial_payload` |
| `kpis.py` | 181 | KPIs agregados, resumo operacional |
| `financeiro.py` | 274 | Parcelas, despesas, custas, fluxo, `marcar_parcela` |
| `prazos.py` | 177 | Audiências, prazos, alertas, centro de atenção |
| `timeline.py` | 249 | Legal Tasks, comunicações, horas, timeline |
| `painel_api.py` | 30 | Facade whitelisted (único path de `xcall`) |

**Total backend painel:** ~1.167 linhas.

### Módulos frontend e linhas

| Módulo | Linhas | Responsabilidade |
|---|---:|---|
| `index.js` | 362 | Bootstrap, load, erro, skeleton |
| `utils.js` | 292 | Helpers, limites 5/10/15, polish chrome |
| `hero.js` | 209 | Header, filtro período (1/7/15/30 dias) |
| `kpis.js` | 519 | Render KPIs e resumo |
| `audiencias.js` | 218 | Centro de atenção, alertas |
| `timeline.js` | 427 | Agenda, tarefas, comunicações |
| `financeiro.js` | 453 | Zona financeira (Manager only) |
| `painel.js` (page) | 13 | Shell Frappe Page |

**Total frontend painel:** ~2.493 linhas (+ `painel.css`).

**Assets:** registrados em `hooks.py` → `app_include_js` (7 módulos painel + utils globais).

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
| `periodo_dias`, `list_limits`, `list_meta` | `__init__` | ✅ | ✅ |
| `kpis` | kpis.py | completo | sem chaves financeiras |
| `resumo` | kpis.py | completo | sem valores financeiros |
| `financeiro` | financeiro.py | ✅ | ❌ omitido |
| `alertas`, `centro_atencao` | prazos.py | ✅ | ✅ |
| `timeline`, `tarefas` | timeline.py | ✅ | ✅ |
| `parcelas` | financeiro.py | ✅ | ❌ |
| `despesas_pendentes`, `total_despesas_mes` | financeiro.py | ✅ | ❌ |
| `custas_pendentes_repasse`, `total_custas_mes` | financeiro.py | ✅ | ❌ |
| `comunicacoes_pendentes`, `ultimas_comunicacoes` | timeline.py | ✅ | ✅* |
| `horas_semana`, `horas_periodo` | timeline.py | ✅ | ✅* |
| `audiencias`, `prazos` | prazos.py | ✅ | ✅ |

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

**Nomes legíveis:** satélites exibem `title` do Serviço/Client, não IDs crus.

---

## 4.4 Frontend — comportamento por role

| Componente | Manager | User |
|---|---|---|
| Hero + filtro período | ✅ | ✅ |
| KPIs operacionais (clientes, serviços, audiências) | ✅ | ✅ |
| KPIs financeiros (honorários, taxa recebimento) | ✅ | Ocultos (backend + JS) |
| Centro de atenção | ✅ | ✅ |
| Timeline / agenda | ✅ | ✅ |
| Zona financeira (parcelas, gráfico, despesas) | ✅ | Removida do DOM |
| Marcar parcela recebida | ✅ | Botão ausente |
| Navegação `list_nav.goto` | ✅ | ✅ |

**Cores:** Chart.js e cards usam CSS variables Frappe — sem hex hardcoded no JS de produção.

**Refresh:** botão ↺ Atualizar; limites 5/10/15 e filtro de período recarregam payload via xcall **sem reload total** da page (soft refresh, jun/2026).

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
| Engenharia tem `attention.py`/`health.py` separados | 🟢 | Advocacia usa `centro_atencao` em `prazos.py` — equivalente funcional |
| E2E browser automatizado | 🟡 | `test_painel_api.py` + script Playwright `tests/e2e/playwright_flow.py` (manual) |

---

## 4.7 Checklist pós-mudança painel

- [ ] `bench build --app advocacia` após editar `public/js/painel/`
- [ ] `bench --site advocacia.local clear-cache`
- [ ] `bench --site advocacia.local run-tests --app advocacia` — `test_painel_api.py` verde
- [ ] Smoke manual: soft refresh ao mudar período/limites
- [ ] Smoke manual: User sem financeiro · Manager com gráfico

---

*Painel modular desde v0.7.0. Referência de padrão para app irmão: `engenharia/public/js/dashboard/`.*
