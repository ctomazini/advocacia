# Seção 1 — Auditoria de Código Completa

**App:** `advocacia` · **Versão:** 0.7.0 · **Site:** `advocacia.local` · **Data:** 2026-06-07  
**Referência normativa:** `REGRAS_ADVOCACIA.md` (raiz do repo) · Inventário técnico: `CODEBASE.md`

---

## 1.1 Conformidade com checklist pré-deploy

| Item | Status | Detalhes |
|---|---|---|
| DocTypes `custom: 0` | 🟢 OK | 24/24 JSONs declaram `"custom": 0`, módulo `Advocacia`. |
| DocType names PT congelados | 🟢 OK | Brownfield — nomes em português não renomeados (ex.: `Legal Case`, `Fee Agreement`). |
| Fieldnames `snake_case` | 🟢 OK | Maioria em PT/EN misto funcional (`cliente`, `servico`, `data_vencimento`). Labels UI em português. |
| Zero Server/Client Script no banco | 🟢 OK | Lógica em controllers Python; fixtures exportam Workspace, Notification, Custom Field em `Event`. |
| naming + autoname + title + search | 🟢 OK | Transacionais: `format:PREFIX-{YYYY}-{####}` + `title_field: title` + `show_title_field_in_link: 1`. |
| Links tipados (não Data) | 🟢 OK | Jurisdiction, Court Branch, Court, Case Phase, Client, Serviço — todos `Link`. |
| Ciclo de vida controller | 🟢 OK | `validate()` + `after_insert()` com `titulos.py` nos transacionais principais. |
| Auto-título via titulos.py | 🟢 OK | Formato `{ID} — {descritor}`; `Office Expense` usa `descricao` como descritor. |
| Zero `frappe.db.commit()` fora setup | 🟢 OK | Apenas em `setup/*`, `patches/*`, `titulos.backfill_titulos_vazios()`, `seed_demo.py` (dev). **Nota:** `resync_pagamentos_acordo(..., commit=True)` é whitelisted — ver segurança. |
| `ignore_permissions` com comentário | 🟢 OK | Bloco em `financeiro.py`; comentários em `calendar_sync.py`, `documentos.py`, `setup/*`. Testes usam sem comentário (aceitável). |
| Zero `except Exception: pass` | 🟢 OK | Erros logados ou re-lançados; scheduler trata item a item em `tasks.py`. |
| Zero `eval`/`exec` | 🟢 OK | — |
| Zero API deprecada JS | 🟢 OK | Sem `cur_frm`, `add_fetch`, `$c_obj` no app. |
| Whitelisted + permission | 🟡 Parcial | 22 endpoints; 20 com `has_permission` explícito. Ver seção 1.3. |
| Type hints em whitelists | 🟡 Parcial | `painel_api.py` e timers com hints; `financeiro.py`/`documentos.py` parcial. |
| Queries com limit | 🟡 Parcial | `limit_page_length` em ~40 refs (painel, reports, notificações) — deprecação Frappe v17. |
| Zero N+1 no painel | 🟢 OK | `_servico_lookup`, `_cliente_nome_lookup` em batch em `painel/_helpers.py`. |
| doc_events: um handler/evento | 🟢 OK | `hooks.py`: um handler por par DocType+evento. |
| Tabs não spaces | 🟢 OK | Amostragem `.py`/`.js` usa tabs. |
| Testes com assert real | 🟢 OK | **241** métodos em 35+ arquivos `test_*.py`; E2E Playwright manual em `tests/e2e/`. |

### Inconsistências prioritárias

1. 🟡 **`gerar_pagamento_atos`** delega para `sincronizar_pagamento_atos` sem check na facade — check existe no callee.
2. 🟡 **`limit_page_length`** em massa — migrar para `limit` antes do upgrade v17.
3. 🟡 **Type hints** incompletos em whitelists legados (`financeiro.py`, `documentos.py`).
4. 🟢 **`pyproject.toml`** em `0.7.0` — alinhado ao release tag.

---

## 1.2 Cobertura de testes

**Comando:** `bench --site advocacia.local run-tests --app advocacia`  
**Total:** 241 testes (jun/2026).

| DocType / Módulo | Tem teste? | Nº testes* | Funcionalidades testadas | SEM teste |
|---|---|---|---|---|
| Legal Case | Sim | 10 | CRUD, CNJ, validações, query | permlevel UI |
| Client | Sim | 13 | CPF/CNPJ, contatos, endereços | — |
| Fee Agreement | Sim | 10 | Parcelas, modos, sync | apply UI flow |
| Legal Payment | Sim | 10 | Status, sync, bulk rules | — |
| Service Record | Sim | 8 | Atos, cobrança | — |
| Time Entry | Sim | 15 | Timer, duração, permissões | — |
| Hearing | Sim | 7 | CRUD, status | — |
| Deadline | Sim | 7 | Datas, prioridade | — |
| Legal Task | Sim | 5 | CRUD, concluir | — |
| Case Communication | Sim | 7 | CRUD, tarefa auto | — |
| Court Cost | Sim | 7 | Repasse, status | — |
| Office Expense | Sim | 11 | Categorias, vencimento | — |
| Document Kit | Sim | 6 | Itens, templates | — |
| Cadastros (Jurisdiction, Court Branch, Court, Fase) | Sim | 4–5 cada | CRUD, unique | — |
| Office Settings | Sim | 17 | CNPJ escritório, logo, banco, prazos | — |
| **Child tables** (5) | Parcial | via pai | Contato, Endereco, Parcela, Ato, Kit Item | CRUD isolado |
| **Painel** | Sim | 9 | Payload, limits, permissões | E2E browser |
| **Permissions** | Sim | 6 | User vs Manager, painel redaction | — |
| **Financeiro** | Sim | 7 | Sync acordo, atos, flags | resync commit |
| **Calendar sync** | Sim | 6 | Hearing/Prazo → Event | Google OAuth E2E |
| **Documentos** | Sim | 6 | docxtpl, kits | — |
| **Notificações/Scheduler** | Sim | 14 | Daily jobs, prazos | — |
| **Reports** (6) | Sim | 12 | Smoke por report | edge cases |
| **Validators** | Sim | 16 | CPF, CNPJ, CNJ, telefone, email | — |
| **Titulos** | Sim | 10 | Composição, backfill | — |
| **Seed demo** | Sim | 4 | seed/clear com `DEMO_MARKER` | produção guard |
| **Imports** | Sim | 3 | Whitelist registration | — |

\*Contagens por arquivo `test_*.py`.

### Gaps específicos

| Área | Gap | Severidade |
|---|---|---|
| `agent_api.py` | ✅ 4 endpoints read-only + testes | 🟢 |
| Google Calendar OAuth | Sem teste E2E de integração Google | 🟢 |
| Permlevel campos financeiros | Coberto em backend; UI não testada | 🟢 |

---

## 1.3 Segurança — whitelists

| Endpoint | Módulo | Permission check? | Observação |
|---|---|---|---|
| `get_painel_data` | painel_api.py | ✅ | `Legal Case` read + `throw=True` |
| `marcar_parcela_recebida` | painel_api.py | ✅ | `Legal Payment` write |
| `resync_pagamentos_acordo` | financeiro.py | ✅ | Acordo write |
| `bulk_delete_pagamentos` | financeiro.py | ✅ | Payment delete |
| `gerar_pagamento_atos` | financeiro.py | 🟡 | Delega — check no callee |
| `sincronizar_pagamento_atos` | financeiro.py | ✅ | Service Record write |
| `marcar_recebido` / `cancelar` | financeiro.py | ✅ | Payment write |
| `generate_document` etc. | documentos.py | ✅ | Legal Case/Template read |
| `servico_query` | servico.py | ✅ | Legal Case read |
| `get_resumo_audiencia` | audiencia.py | ✅ | Hearing read |
| `get_resumo_prazo` | controle_de_prazos.py | ✅ | Deadline read |
| `iniciar_timer` / `parar_timer` | registro_de_horas.py | ✅ | write no doc |
| `get_timer_ativo_usuario` | registro_de_horas.py | ✅ | read (retorna None se negado) |
| `concluir` | tarefa.py | ✅ | Legal Task write |
| `marcar_recebida` / `estornar` | parcela_de_honorarios.py | ✅ | Acordo write |
| `criar_despesa_rapida` | despesa_do_escritorio.py | ✅ | create |

**Painel financeiro:** `strip_financial_payload()` omite `financeiro`, `parcelas`, KPIs financeiros para **Advocacia User** — ✅ `test_permissions.py`.

**Roles:** `Advocacia User` (operacional, sem delete Legal Payment) · `Advocacia Manager` (full financeiro).

---

## 1.4 Deprecation warnings

### `limit_page_length` (v17 → usar `limit`)

| Área | Ocorrências aprox. |
|---|---:|
| `painel/` (kpis, prazos, financeiro, timeline) | 20 |
| Script Reports (6) | 13 |
| `notificacoes.py`, `servico.py`, `seed_demo.py` | 7 |

**Ação recomendada:** migrar painel e reports antes do upgrade Frappe v17.

### APIs deprecadas JS

| Padrão | Ocorrências |
|---|---:|
| `cur_frm` | 0 |
| `add_fetch` | 0 |
| `$c_obj` | 0 |

---

## 1.5 Métricas do repositório

| Métrica | Valor |
|---|---:|
| DocTypes | 24 |
| Linhas Python | ~10.949 |
| Linhas JavaScript | ~5.116 |
| Script Reports | 6 |
| Arquivos de teste | 34 |
| Métodos de teste | 241 |
| Whitelists | 22 |
| `doc_events` handlers | 6 pares DocType+evento |
| Scheduler daily | 5 jobs |
| Scheduler weekly | 1 job |
| Field descriptions | 218 / 232 campos elegíveis (94%) |

---

## 1.6 Seed demo (dev only)

| Item | Detalhe |
|---|---|
| Módulo | `setup/seed_demo.py` (~919 linhas) |
| Marcador | `DEMO_MARKER = "_DEMO_"` |
| Comandos | `bench seed-demo-advocacia`, `bench clear-demo-advocacia` |
| Produção | **Proibido** — comentário explícito no topo do módulo |
| Testes | `test_seed_demo.py` (4 testes) |

---

*Auditoria read-only. Próxima revisão recomendada após deploy v0.7.0 ou upgrade Frappe v17.*
