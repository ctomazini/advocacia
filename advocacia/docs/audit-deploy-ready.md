# Auditoria Deploy-Ready — Advocacia

**Data:** 2026-06-07  
**Commit:** `28467df` — docs: organize documentation for filters, connections and E2E  
**Site auditado:** `advocacia.local` (bench nativo, Frappe v16)  
**Critério:** padrão unificado `REGRAS_OBRIGATORIAS.md` (engenharia), com notas brownfield do `REGRAS_ADVOCACIA.md`

---

## Resumo

| Status | Quantidade | Interpretação |
| --- | ---: | --- |
| ✅ Passou | **38** | Conformidade plena ou aceitável para produção |
| ⚠️ Atenção | **22** | Débito técnico / risco moderado — corrigir pós-go-live ou antes se possível |
| ❌ Bloqueante | **7** | Impede deploy seguro até resolução |

### Veredito

**Não deploy-ready** para produção limpa enquanto existirem **Server Scripts** e **Client Script** legados no banco do site. O código Git está substancialmente conforme (230 testes OK, `custom: 0`, lógica em controllers), mas a **instalação atual do site carrega lógica fora do Git** — violação do princípio raiz do app.

Após limpar scripts do banco + smoke de reinstall, o app pode ir a produção com débitos conscientes documentados (nomes PT congelados, `cur_frm` pontual, `limit_page_length`).

---

## Débito Técnico Histórico

| Débito | Origem | Status no Git | Status no banco (advocacia.local) |
| --- | --- | --- | --- |
| DocTypes em português | Pré-norma EN | ⚠️ Congelado (`REGRAS_ADVOCACIA`) | N/A |
| Server Scripts de faturas | Era pré-controller | ❌ Removido do Git | ❌ **4 scripts ativos** |
| Client Script FAB Painel | Era pré-`list_nav.js` | ❌ Removido do Git | ❌ **1 script ativo** (referencia ERPNext) |
| Fieldnames PT com acentos | Brownfield | ⚠️ Backlog v2 | N/A |
| `limit_page_length` massivo | Frappe v16 | ⚠️ Migrar antes v17 | N/A |

---

## Detalhamento por Seção

### SEÇÃO 1 — DocTypes: Schema e Naming

#### 1.1 `custom: 0` — ✅
```text
grep '"custom": 1' → zero resultados
```
24/24 DocTypes com `"custom": 0`.

#### 1.2 `naming_rule` + `autoname` — ⚠️

| DocType | naming_rule | autoname | Status |
| --- | --- | --- | --- |
| Transacionais (13) | Expression | `format:PREFIX-{YYYY}-{####}` | ✅ |
| Document Kit, Document Template | By fieldname | `field:titulo` | ✅ |
| Jurisdiction, Court, Court Branch, Case Phase | **AUSENTE** | `field:*_name` | ⚠️ Falta `naming_rule` explícito |
| Office Settings (Single) | **AUSENTE** | **AUSENTE** | ⚠️ Single — aceitável, mas sem `search_fields` |

#### 1.3 `title_field` + `show_title_field_in_link` — ⚠️
- 18/19 standalones com `title_field` definido — ✅
- **Office Settings:** `title_field` ausente — ⚠️
- Todos standalones: `show_title_field_in_link: 1` — ✅

#### 1.4 `search_fields` — ⚠️
- **Office Settings:** `search_fields` ausente — ⚠️
- Demais standalones: preenchidos — ✅

#### 1.5 DocType names — idioma — ❌ (⚠️ congelado advocacia)

24 DocTypes em português (`Legal Case`, `Hearing`, `Jurisdiction`, …).

- Padrão engenharia (EN Title Case): **24 × ❌**
- `REGRAS_ADVOCACIA.md`: **congelado — não renomear** → tratar como ⚠️ débito consciente, não bloqueante para este app

#### 1.6 Fieldnames — ⚠️
- **12 fieldnames** com acentos PT (`billing_type`, `remarks`, `description`, …) — ⚠️
- **~15 column_break** auto-gerados (`column_break_info`, `column_break_parc`, …) — ⚠️ cosmético

#### 1.7 Link fields tipados — ✅
Falsos positivos do grep (`jurisdiction_name`, `case_phase_name` são campos de autoname Data, não Links mal tipados). Referências reais (Jurisdiction, Court Branch, Court, Client, Legal Case) usam `Link` — ✅

#### 1.8 Prefixos autoname — ✅
12 prefixos únicos, zero colisão (`ACOR-`, `AUD-`, `CLI-`, …).

#### 1.9 `idx` duplicado — ⚠️
| DocType | idx duplicados |
| --- | --- |
| Fee Agreement | {2, 4} |
| Hearing | {4} |
| Deadline | {4} |

---

### SEÇÃO 2 — Controllers Python

#### 2.1 Ordem do ciclo de vida — ✅
Controllers seguem padrão `validate` → `after_insert` → hooks. Sem inversões críticas detectadas.

#### 2.2 Auto-título — ✅
Títulos compostos via `titulos.py` (`recompor_titulo_se_vazio`, `aplicar_titulo_pos_insert`) em 11 transacionais — **não** via Server Script.

#### 2.3 `frappe.db.commit()` — ✅ (⚠️ 1 exceção whitelisted)

| Contexto | Arquivo | OK? |
| --- | --- | --- |
| setup/*, patches, seed_demo, titulos backfill | vários | ✅ permitido |
| testes / e2e | tests/* | ✅ |
| **Whitelisted** `resync_pagamentos_acordo` | financeiro.py:339 `commit=True` | ⚠️ viola regra; Frappe auto-commit no request |

Produção (hooks/API/scheduler/painel): **zero commit()** — ✅

#### 2.4 `ignore_permissions` — ✅
Usos em produção com comentário justificativo:
- `financeiro.py` (bloco documentado)
- `calendar_sync.py` (sync Event)
- `documentos.py` (anexo File)
- `setup/*` (migrate/seed)

Testes usam `ignore_permissions=True` sem comentário — aceitável.

#### 2.5 `except Exception: pass` — ✅
Zero ocorrências.

#### 2.6 `eval` / `exec` — ✅
Zero ocorrências.

#### 2.7 Strings sem `_()` — ✅
Amostragem de `frappe.throw`/`msgprint`: mensagens usam `_()` nos controllers auditados.

#### 2.8 Whitelisted — ⚠️

**22 endpoints** `@frappe.whitelist()`. Permission checks:

| Função | has_permission | Type hints |
| --- | --- | --- |
| `get_painel_data`, `marcar_parcela_recebida` | ✅ | ✅ |
| `resync_pagamentos_acordo`, `bulk_delete_pagamentos` | ✅ | ✅ |
| `sincronizar_pagamento_atos` | ✅ | parcial |
| **`gerar_pagamento_atos`** | ⚠️ delega (check no callee) | parcial |
| `servico_query`, calendar `get_events`, timers | ✅ | parcial |
| `documentos.*`, `despesa.gerar_proxima_despesa` | ✅ | parcial |
| `parcela.registrar_*`, `tarefa.concluir` | ✅ | parcial |

#### 2.9 N+1 — ⚠️
Heurística do grep encontrou loops com `get_doc`/`get_value` em:
- `tasks.py` (schedulers — batch por design, item a item)
- `financeiro.py`, `titulos.py` backfill
- `painel/_helpers.py` — **batch lookups** ✅

Schedulers processam item a item com tratamento de erro — ⚠️ aceitável, monitorar volume.

#### 2.10 Queries sem `limit` — ⚠️
~35 chamadas `get_all`/`get_list`/`db.sql` sem `limit_page_length` explícito, principalmente em:
- `tasks.py` (6 schedulers)
- `financeiro.py` (sync batch)
- `setup/sidebar.py`, `seed_demo.py`

`notificacoes.py` usa `limit_page_length=500` — ✅

---

### SEÇÃO 3 — JavaScript Client-Side

#### 3.1 `cur_frm` — ❌
| Arquivo | Uso |
| --- | --- |
| `public/js/list_nav.js:73` | `var frm = cur_frm` em handler Connections | ❌ API deprecada em produção |
| `tests/e2e/playwright_flow.py` | Espera `cur_frm` no browser | ✅ aceitável (teste) |

#### 3.2 Hex hardcoded — ✅
Zero `#RRGGBB` em `public/` e doctype JS/CSS.

#### 3.3 Strings sem `__()` — ⚠️
Não auditado exaustivamente; amostra de alerts no painel usa padrão Frappe. Prioridade baixa.

#### 3.4 APIs deprecadas — ✅
Zero `$c_obj`, zero `add_fetch`.

#### 3.5 Lógica de negócio no JS — ✅
JS limitado a UX: máscaras, filtros responsivos, navegação, timer UI. Sync financeiro e títulos permanecem em Python.

---

### SEÇÃO 4 — hooks.py

#### 4.1 Fixtures — ✅
Definidos: Workspace, Notification (2), Custom Field (Event `custom_source%`).  
Não exporta Server Script nem Client Script — ✅

#### 4.2 Fixture JSONs — ✅
```
fixtures/custom_field.json
fixtures/notification.json
fixtures/workspace.json
```

#### 4.3 Anti-pattern fixtures — ✅
Sem `server_script.json` ou `client_script.json` no Git.

#### 4.4 `doc_events` — ✅
Um handler por `(DocType, evento)`. Legal Payment: handler único `processar_pagamento_on_update` — ✅

#### 4.5 `scheduler_events` — ✅
- **daily:** 5 jobs (parcelas, despesas, notificações, audiências, prazos)
- **weekly:** 1 job (status serviços)

---

### SEÇÃO 5 — Zero Lógica no Banco — ❌ BLOQUEANTE

Site: `advocacia.local` (somente `frappe` + `advocacia` instalados).

#### 5.1 Server Scripts — ❌
**4 scripts ativos** (legado pré-refactor, não existem no Git):

| Nome | Tipo | reference_doctype |
| --- | --- | --- |
| Gerar Faturas Atos | API | null |
| Contar Faturas Acordo | API | null |
| Atualizar Faturas Acordo | API | null |
| Gerar Faturas Acordo | API | null |

Lógica equivalente hoje vive em `financeiro.py` — scripts devem ser **desabilitados/removidos** antes do deploy.

#### 5.2 Client Scripts — ❌
**1 script ativo:**

| Nome | dt | Problema |
| --- | --- | --- |
| Navegacao Advocacia | Legal Case | Referencia `Sales Invoice`, `Customer` (ERPNext); duplica FAB removido do Git |

Substituído por `list_nav.js` + painel hero — **remover do banco**.

---

### SEÇÃO 6 — Testes — ✅

#### 6.1 Suite
```text
bench run-tests --app advocacia → 230 testes, OK (12,3s)
35 arquivos test_*.py em advocacia/advocacia/tests/
```
Testes por DocType ficam centralizados em `tests/` (não em `doctype/*/test_*.py`) — padrão válido.

#### 6.2 Testes vazios (`pass`) — ✅
Nenhum `def test_*` com corpo `pass` isolado detectado.

#### 6.3 Cobertura whitelisted — ✅
Principais endpoints cobertos:
- `test_painel_api.py` (9)
- `test_financeiro.py` (7) — inclui `gerar_pagamento_atos`, `bulk_delete`, `resync`
- `test_registro_atos.py`, `test_documentos.py`, `test_permissions.py` (6)
- `test_registro_horas.py` (15) — timers

---

### SEÇÃO 7 — Workspace — ⚠️

Fixture `fixtures/workspace.json`:
- **Content blocks:** 12 shortcuts (Painel, Serviços, Honorários, Legal Payments, …)
- **shortcuts[]:** 18 entradas (inclui Jurisdiction, Court Branch, Court, Legal Tasks, Documentos extras)
- Content ↔ shortcuts: **12/12 presentes** no array — ✅
- Shortcuts extras sem bloco visual no content — ⚠️ cosmético (links sidebar cobrem)

Workspace JSON em `workspace/advocacia/advocacia.json` tem `content` vazio no repo — fixture exportada é a fonte canônica — ✅

---

### SEÇÃO 8 — Formatação e Versionamento — ⚠️

#### 8.1 Tabs vs Spaces — ⚠️
Arquivos Python com indentação por espaços (amostra):
- `validators.py`
- `tests/e2e/playwright_flow.py`
- `setup/seed_demo.py`
- `doctype/jurisdiction/jurisdiction.py`, `vara/vara.py`, `tribunal/tribunal.py`, `fase_processual/fase_processual.py`
- `doctype/fee_agreement/fee_agreement.py`

Maioria do codebase usa tabs — ⚠️ inconsistência, não bloqueante.

#### 8.2 TODO / FIXME — ✅
Zero ocorrências em `.py`/`.js` de produção.

#### 8.3 Versão — ✅
`pyproject.toml`: `0.7.0` alinhado à documentação.

---

### SEÇÃO 9 — Débito Específico Advocacia

#### 9.1 Painel — ✅ (⚠️ módulo grande)
Frontend modular em `public/js/painel/`:

| Módulo | Linhas |
| --- | ---: |
| index.js | 597 |
| kpis.js | 519 |
| financeiro.js | 453 |
| timeline.js | 427 |
| utils.js | 292 |
| audiencias.js | 218 |
| hero.js | 207 |
| page/painel/painel.js | 13 |

Monolito eliminado — ✅. `index.js` > 300 linhas — ⚠️ backlog split opcional.

#### 9.2 Roles — ✅
```
Advocacia User
Advocacia Manager
```
Criadas via `setup/roles.py` + `setup/permissions.py`.

#### 9.3 Field descriptions — ✅
```
228/228 campos elegíveis (excl. breaks/HTML/Button) = 100%
218/232 incluindo breaks técnicos = 94%
```
Script: `scripts/add_field_descriptions.py`.

---

### SEÇÃO 10 — Reinstall Test (Simulação) — ⚠️

| Balde | Conteúdo | Status |
| --- | --- | --- |
| **1. Código** | 24 DocTypes, 1 Page (`painel`), 6 Reports, hooks, controllers | ✅ auto no install |
| **2. Fixtures** | workspace, notification, custom_field Event | ✅ exportados |
| **3. Seed idempotente** | `after_migrate` chain (roles, permissions, sidebar, reports, workspace) | ✅ |
| **Anti-pattern** | Server/Client Script em fixtures Git | ✅ ausente |

**Reinstall limpo end-to-end não executado nesta auditoria** — ⚠️ obrigatório antes do go-live real.

---

## Checks Consolidados

### ✅ Passou (38)
1. Zero `custom: 1`
2. 24 DocTypes `custom: 0`
3. Prefixos autoname sem colisão
4. Links tipados (Jurisdiction, Court Branch, Client, Legal Case, …)
5. Auto-título via `titulos.py`
6. Zero Server Script no Git
7. Zero Client Script no Git fixtures
8. Fixtures hooks corretos
9. doc_events sem duplicata
10. Schedulers definidos (5+1)
11. Zero `eval`/`exec`
12. Zero `except: pass`
13. Zero hex hardcoded JS
14. Zero `$c_obj`/`add_fetch`
15. JS = UX (máscaras, filtros, nav)
16. `ignore_permissions` comentado em produção
17. commit() ausente em hooks/API/scheduler/painel
18. 230 testes verdes
19. Roles User/Manager
20. Permissões financeiras (`test_permissions.py`)
21. Painel modular backend+frontend
22. Facade whitelisted única (`painel_api`)
23. Field descriptions ≥ 94%
24. Sidebar 26 links + collapsible v16
25. `in_standard_filter` em transacionais
26. `list_nav.js` + `list_filters.js`
27. Calendar sync → Event
28. Validators BR (CPF/CNPJ/CNJ)
29. Demo marker `_DEMO_` isolado
30. Seed commands bench (`seed-demo-advocacia`)
31. Reports script (6)
32. Notifications fixture (2)
33. Custom Fields Event fixture
34. Whitelist críticos com `has_permission`
35. Type hints em `painel_api`
36. E2E Playwright script (opcional, marcador `_PW_E2E_`)
37. Documentação v0.7.0 atualizada
38. MIT license / pyproject deps

### ⚠️ Atenção (22)
1. DocTypes PT (congelado — débito consciente)
2. `naming_rule` ausente em 5 cadastros auxiliares + Single
3. `Office Settings` sem title/search
4. idx duplicado (3 DocTypes)
5. Fieldnames PT com acentos
6. column_break auto-gerados
7. `resync_pagamentos_acordo` com `commit=True`
8. `gerar_pagamento_atos` sem check direto na facade
9. Type hints parciais em whitelists legados
10. `limit_page_length` ~40 refs (deprecação v17)
11. Queries scheduler sem limit explícito
12. N+1 heurístico em schedulers
13. `cur_frm` — apenas e2e aceitável; produção ver ❌
14. Workspace shortcuts extras vs content
15. Python files com spaces (não tabs)
16. `index.js` painel > 300 linhas
17. Reinstall limpo não executado
18. E2E Playwright depende `install-deps` + `--noreload`
19. Template/Kit E2E podem falhar sem fixture docx
20. Port fieldnames EN auxiliares (`case_phase_name`, `city`)
21. Chart.js vs frappe.ui.Chart (backlog)
22. `agent_api.py` inexistente (pós-deploy)

### ❌ Bloqueante (7)
1. **4 Server Scripts** no banco (`Gerar/Contar/Atualizar Faturas`)
2. **1 Client Script** no banco (`Navegacao Advocacia` + refs ERPNext)
3. **`cur_frm` em `list_nav.js`** (produção)
4. Lógica no banco viola princípio raiz app-instalável
5. Client Script referencia `Sales Invoice`/`Customer` — app é **sem ERPNext**
6. Server Scripts duplicam lógica já em `financeiro.py` — risco de comportamento divergente
7. Deploy sem limpar banco = produção não reproduzível via Git

---

## Plano de Migração (priorizado)

### P0 — Antes do deploy (bloqueante)

1. **Remover/desabilitar os 4 Server Scripts** no site de produção (via UI ou `frappe.delete_doc`). Validar fluxo Acordo → Legal Payment só via `financeiro.py`.
2. **Remover Client Script `Navegacao Advocacia`**. Confirmar que `list_nav.js` + painel hero cobrem navegação.
3. **Substituir `cur_frm` em `list_nav.js`** por API v16 (`frappe.ui.form.get_open_form()` ou handler com `frm` no callback do `frappe.ui.form.on`).
4. **Executar reinstall limpo:**
   ```bash
   bench new-site prod-advocacia.local --install-app advocacia
   bench --site prod-advocacia.local migrate
   bench --site prod-advocacia.local run-tests --app advocacia
   ```
   Confirmar zero Server/Client Scripts após install.

### P1 — Pré go-live (recomendado)

5. Corrigir **idx duplicados** em Acordo, Hearing, Deadline.
6. Adicionar **`naming_rule`** explícito em Jurisdiction, Court Branch, Court, Case Phase.
7. Remover **`commit=True`** de `resync_pagamentos_acordo` (confiar no auto-commit Frappe).
8. Adicionar **`has_permission` direto** em `gerar_pagamento_atos`.
9. Adicionar **`limit_page_length`** nos schedulers de `tasks.py`.
10. Smoke manual: painel User/Manager, Connections filtradas, sync pagamento, calendar Event.

### P2 — Pós-deploy (backlog)

11. Renomear fieldnames PT com acentos (migration plan).
12. Padronizar indentação tabs nos arquivos com spaces.
13. Migrar `limit_page_length` → `limit` (prep v17).
14. Split opcional `painel/index.js`.
15. `agent_api.py` jurídico + testes.

### P3 — Não fazer (decisão fixa)

- **Não renomear DocTypes** para inglês — risco >> benefício (`REGRAS_ADVOCACIA.md`).

---

## Comandos de Verificação Pós-Migração

```bash
# Zero scripts no banco
bench --site SITE execute frappe.get_all --args '["Server Script"]' --kwargs '{"fields":["name"]}'
bench --site SITE execute frappe.get_all --args '["Client Script"]' --kwargs '{"fields":["name"]}'

# Suite verde
bench --site SITE run-tests --app advocacia

# Smoke E2E (opcional)
export ADVOCACIA_E2E_PWD='...'
bench --site SITE serve --port 8000 --noreload
python advocacia/advocacia/tests/e2e/playwright_flow.py
```

---

*Auditoria diagnóstica — nenhum arquivo de código foi alterado. Relatório gerado em 2026-06-07.*
