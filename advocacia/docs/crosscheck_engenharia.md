# Cross-audit: advocacia ↔ engenharia

> **Snapshot 2026-06-06 (referência histórica).** Vários itens foram resolvidos na v0.7.0 — ver [REGRAS_ADVOCACIA.md](../../REGRAS_ADVOCACIA.md), [advocacia/docs/README.md](./README.md) e `audit_*.md`.

### Atualizações pós-snapshot (jun/2026)

| Item no snapshot abaixo | Status atual (advocacia) |
| --- | --- |
| Sem `REGRAS_ADVOCACIA.md` | ✅ Criado |
| Field descriptions 5,2% | ✅ 94% (218/232) |
| Frontend painel monolítico 4097 linhas | ✅ Modular `public/js/painel/` (~2.500 linhas) |
| Sem `bench seed-demo` | ✅ `seed-demo-advocacia` / `clear-demo-advocacia` |
| Sem `test_permissions.py` | ✅ 6 métodos |
| Sem `list_filters` | ✅ `list_filters.js` + CSS responsivo |
| Connections lista genérica | ✅ `list_nav.js` filtra por documento pai |
| 222 testes | ✅ **230** testes (jun/2026) |

**Data original:** 2026-06-06  
**Escopo:** comparação read-only de padrões entre os apps Frappe v16 `advocacia` (brownfield, PT) e `engenharia` (greenfield, EN).  
**Paths inspecionados:**
- `/home/frappe/frappe-bench/apps/advocacia`
- `/home/frappe/frappe-bench/apps/engenharia`

**Execução de testes:**
- `bench --site advocacia.local run-tests --app advocacia` → **230 testes, OK** (jun/2026)
- `bench --site advocacia.local run-tests --app engenharia` → **falhou** (`DocType Document Kit not found` — app não instalado neste site)

---

## 1. Tabela resumo

| Categoria | Engenharia | Advocacia | Recomendação | Esforço |
| --- | --- | --- | --- | --- |
| **1. Infraestrutura de código** | `REGRAS_OBRIGATORIAS.md` (515 linhas); 38 DocTypes EN | `REGRAS_ADVOCACIA.md` + `CODEBASE.md`; 24 DocTypes PT | Paridade documental OK | — |
| **1.1 REGRAS equivalente** | Sim (`REGRAS_OBRIGATORIAS.md`) | ✅ `REGRAS_ADVOCACIA.md` | — | — |
| **1.2 Naming conventions** | DocTypes EN; fieldnames `snake_case` EN | DocTypes PT congelados; 148 fieldnames distintos, maioria PT (`cliente`, `servico`, `descricao`, `valor`, …) | Manter PT no advocacia; usar engenharia só como referência de *padrão*, não de idioma | — |
| **1.3 `custom: 0` explícito** | 38/38 JSONs | 24/24 JSONs | Nenhuma ação — paridade OK | Quick win (n/a) |
| **1.4 Deprecations** | `cur_frm`/`add_fetch`/`$c_obj`: 0; `limit_page_length`: 4 refs (dashboard) | Mesmas deprecations: 0; `limit_page_length`: **40 refs** em 16 arquivos `.py` | Advocacia já conforme; engenharia pode expandir caps em reports/APIs | Quick win |
| **2. Títulos e naming IDs** | `titles.py`; descritores por domínio (obra, medição, comissão) | `titulos.py`; descritor = cliente ou `descricao` | Paridade estrutural OK; advocacia pode enriquecer descritores por DocType como engenharia | Médio |
| **3. Roles e permissões** | `setup/roles.py` + `setup/permissions.py`; dashboard filtra Manager | ✅ `permissions.py` + `strip_financial_payload` + `test_permissions.py` | Paridade OK | — |
| **3.2 Whitelist audit** | 25 endpoints; 21 com `has_permission`; 19 com type hints | 21 endpoints; 14 com `has_permission`; 0 type hints | Fechar gaps: `painel_api`, timers, parcelas, `tarefa.concluir` | Médio |
| **4. Dashboard / Painel** | Backend modular (12 arquivos); frontend modular (~999 linhas JS) | Backend modular (7 arquivos); frontend modular `public/js/painel/` (~2.500 linhas) | Paridade estrutural OK; soft refresh jun/2026 | — |
| **4.2 KPIs** | Obras, protocolos, margem, comissões, reembolsáveis | Clients, serviços, audiências, honorários, custas, taxa recebimento | Manter KPIs de domínio; opcional: tiles de atenção/saúde como engenharia | Médio |
| **5. Calendar sync** | `Deadline` + `Permit` → `Event` | `Hearing` + `Deadline` → `Event` | Paridade OK; testes em ambos (`test_calendar_sync.py`) | — |
| **6. Testes** | 192 métodos; `test_permissions`, `test_agent_api` | **230** métodos; `test_permissions`, `test_painel_api` | Adicionar `test_agent_api.py` jurídico | Médio |
| **7. Connections / Links** | Hub `Construction Project`; 12 satélites | Hub `Legal Case`; 9 satélites; lista filtrada (`list_nav.js`) | Engenharia pode portar `list_nav` | Médio |
| **8. Field descriptions** | 346/352 (98,3%) | 218/232 (94%) | Paridade aceitável | — |
| **9. Hooks e scheduler** | 7 `doc_events`; scheduler daily (1 job) | 6 `doc_events`; scheduler daily (5) + weekly (1) | Advocacia mais completo em notificações; sem duplicatas de handler | Quick win (documentar) |
| **10. Geração de documentos** | `documents.py` (492 linhas); kits + templates | `documentos.py` (601 linhas); kits + templates | Paridade; engenharia tem placeholders de obra | — |
| **11. Navegação (FAB + Header)** | `quick_actions.js`; sem `list_nav.js` | `list_nav.js` + `list_filters.js` + painel hero | Portar navegação filtrada para engenharia | Médio |
| **12. Demo data seeder** | `bench seed-demo` / `clear-demo` | `bench seed-demo-advocacia` / `clear-demo-advocacia` | Paridade OK (nomes distintos) | — |
| **13. AI readiness** | `agent_api.py` (3 endpoints) + `test_agent_api.py` + `docs/audit_ai_readiness.md` | **Inexistente** | Criar `agent_api.py` jurídico (`get_active_servicos`, resumo financeiro condicional) | Longo |

---

## 2. Detalhamento por categoria

### 1. Infraestrutura de código

#### 1.1 `REGRAS_OBRIGATORIAS.md` equivalente

| App | Arquivo | Conteúdo |
| --- | --- | --- |
| Engenharia | `engenharia/REGRAS_OBRIGATORIAS.md` | Checklist normativo fechado (515 linhas): naming EN, um DocType/commit, disciplinas §9 |
| Advocacia | `advocacia/CODEBASE.md` | Inventário técnico gerado (626 linhas), útil mas não normativo |
| Advocacia | `advocacia/ENGENHARIA_STANDARDS.md` | Cópia da norma do **outro** app — não governa advocacia |

**Conclusão:** advocacia carece de documento operacional equivalente ao `REGRAS_OBRIGATORIAS.md`.

#### 1.2 Naming conventions — DocTypes advocacia (24)

Todos em português, módulo `Advocacia`, `custom: 0`:

| DocType | Tipo |
| --- | --- |
| Fee Agreement | transacional |
| Legal Act Item | child |
| Hearing | transacional |
| Client | cadastro |
| Jurisdiction | cadastro rígido |
| Case Communication | transacional |
| Office Settings | settings |
| Client Contact | child |
| Deadline | transacional |
| Court Cost | transacional |
| Office Expense | transacional |
| Client Address | child |
| Case Phase | cadastro |
| Document Kit | cadastro |
| Document Kit Item | child |
| Legal Payment | transacional |
| Fee Installment | child |
| Service Record | transacional |
| Time Entry | transacional |
| Legal Case | hub |
| Legal Task | transacional |
| Document Template | cadastro |
| Court | cadastro |
| Court Branch | cadastro |

**Fieldnames:** 232 campos úteis, 148 fieldnames distintos. Padrão dominante PT: `cliente` (10×), `servico` (9×), `descricao`/`description`, `valor`, `data_*`, `status`. Engenharia usa espelho EN (`customer`, `project`, `description`, `amount`).

#### 1.3 `custom: 0` explícito

```bash
# Verificação 2026-06-06
advocacia: 24 JSONs — 0 faltando "custom": 0
engenharia: 38 JSONs — 0 faltando "custom": 0
```

#### 1.4 Deprecations (grep advocacia)

| Padrão | Ocorrências |
| --- | ---: |
| `limit_page_length` | 40 (painel, reports, notificações, servico query) |
| `cur_frm` | 0 |
| `add_fetch` | 0 |
| `$c_obj` | 0 |

Engenharia: `limit_page_length` apenas em `dashboard/__init__.py` e `dashboard_api.py` (4 refs). Reports engenharia não foram auditados neste grep — advocacia usa `limit_page_length=0` em Script Reports (padrão aceito Frappe).

---

### 2. Títulos e naming IDs

#### 2.1 Composição de títulos

Ambos seguem `{ID} — {descritor}` com separador `" — "`:

| | Advocacia (`titulos.py`) | Engenharia (`titles.py`) |
| --- | --- | --- |
| Descritor padrão | Nome do `Client` | Nome do `Customer` |
| Fallback | `descricao` ou DocType | `description` ou lógica por DocType |
| Flag especial | `Office Expense`: `usar_descricao=True` | Vários DocTypes com `_resolve_descriptor` customizado |
| Pós-insert | `aplicar_titulo_pos_insert` | `apply_title_post_insert` |
| Validate | `recompor_titulo_se_vazio` | `recompose_title` |
| Backfill | `backfill_titulos_vazios()` com `commit()` | Não exposto |

#### 2.2 Tabela naming por DocType (advocacia)

| DocType | naming_rule | autoname | title_field | show_in_link | search_fields |
| --- | --- | --- | --- | ---: | --- |
| Fee Agreement | Expression | `format:ACOR-{YYYY}-{####}` | title | 1 | title,cliente,status |
| Legal Act Item | — | — | — | 0 | — |
| Hearing | Expression | `format:AUD-{YYYY}-{####}` | title | 1 | title,cliente,status_aud |
| Client | Expression | `format:CLI-{YYYY}-{####}` | nome | 1 | nome,cpf,cnpj |
| Jurisdiction | — | field:jurisdiction_name | jurisdiction_name | 1 | jurisdiction_name,uf |
| Case Communication | Expression | `format:COM-{YYYY}-{####}` | title | 1 | assunto,cliente,tipo |
| Office Settings | — | — | — | 1 | — |
| Client Contact | — | — | — | 0 | — |
| Deadline | Expression | `format:PRAZO-{YYYY}-{####}` | title | 1 | descricao,cliente,status |
| Court Cost | Expression | `format:CUST-{YYYY}-{####}` | title | 1 | descricao,cliente,status |
| Office Expense | Expression | `format:DESP-{YYYY}-{####}` | title | 1 | descricao,categoria,status |
| Client Address | — | — | — | 0 | — |
| Case Phase | — | field:case_phase_name | case_phase_name | 1 | case_phase_name |
| Document Kit | By fieldname | field:titulo | titulo | 1 | titulo |
| Document Kit Item | — | — | — | 0 | — |
| Legal Payment | Expression | `format:PAG-{YYYY}-{####}` | title | 1 | descricao,cliente,status,data_vencimento |
| Fee Installment | — | — | — | 0 | — |
| Service Record | Expression | `format:ATOS-{YYYY}-{####}` | title | 1 | title,cliente,status |
| Time Entry | Expression | `format:HRS-{YYYY}-{####}` | title | 1 | atividade,cliente,data |
| Legal Case | Expression | `format:SERV-{YYYY}-{####}` | title | 1 | title,cliente,numero_processo,status |
| Legal Task | Expression | `format:TAR-{YYYY}-{####}` | title | 1 | titulo,cliente,status |
| Document Template | By fieldname | field:titulo | titulo | 1 | titulo,tipo_documento |
| Court | — | field:court_name | court_name | 1 | court_name,abbreviation |
| Court Branch | — | field:court_branch_name | court_branch_name | 1 | court_branch_name,comarca |

**List views:** 12 transacionais com `hide_name_column: true` (engenharia: 13).

---

### 3. Roles e permissões

#### 3.1 Arquitetura

| Aspecto | Engenharia | Advocacia |
| --- | --- | --- |
| Roles | `Engenharia User`, `Engenharia Manager` — seed em `setup/roles.py` + fixture | `Advocacia User`, `Advocacia Manager` — só `setup/install.py` |
| Permissões programáticas | `setup/permissions.py` (~190 linhas): FINANCIAL / CATALOG / OPERATIONAL split | **Ausente** — permissões só via DocType JSON padrão |
| permlevel financeiro | Campos `permlevel: 1` em `Construction Project` + Custom DocPerm Manager-only | Apenas `permlevel: 0` explícito nos JSONs auditados |
| Dashboard role filter | `user_is_engenharia_manager()` oculta KPIs/listas financeiras | `get()` exige `Legal Case` read; **financeiro exposto a User** |
| Notificações | Templates engenharia | Filtra destinatários por role `Advocacia Manager` em `notificacoes.py` |

#### 3.2 Audit `@frappe.whitelist()`

| Métrica | Engenharia | Advocacia |
| --- | ---: | ---: |
| Total endpoints | 25 | 21 |
| Com `has_permission` | 21 (84%) | 14 (67%) |
| Com type hints | 19 (76%) | 0 (0%) |

**Gaps advocacia (sem `has_permission` no corpo da função):**

| Arquivo | Função |
| --- | --- |
| `painel_api.py` | `get_painel_data`, `marcar_parcela_recebida` |
| `doctype/fee_installment/fee_installment.py` | `registrar_recebimento`, `registrar_repasse` |
| `doctype/legal_task/legal_task.py` | `concluir` |
| `doctype/time_entry/time_entry.py` | `iniciar_timer`, `parar_timer` |

*Nota:* `painel/__init__.py` valida permissão internamente; a facade `painel_api.py` não — diverge do padrão engenharia (`dashboard_api.py` valida na facade).

---

### 4. Dashboard / Painel

#### 4.1 Estrutura

| Camada | Advocacia | Engenharia |
| --- | --- | --- |
| Facade | `painel_api.py` (26 linhas) | `dashboard_api.py` (31 linhas) |
| Orquestrador | `painel/__init__.py` (110) | `dashboard/__init__.py` (164) |
| Domínios | `_helpers`, `kpis`, `financeiro`, `prazos`, `timeline` | `_helpers`, `kpis`, `financial`, `deadlines`, `timeline`, `attention`, `health`, `operational`, `commissions`, `agenda` |
| Arquivo >150 linhas | `financeiro.py` (275), `timeline.py` (249), `kpis.py` (181) | `kpis.py` (183) |
| Frontend | `page/painel/painel.js` **4097 linhas** | `page/eng_dashboard/eng_dashboard.js` (123) + `public/js/dashboard/*.js` (**999 linhas** total) |
| N+1 | Lookups em lote em `_helpers.py` (`_servico_lookup`, `_cliente_nome_lookup`) | Mesmo padrão (`_project_lookup`, `_customer_name_lookup`) |
| CSS vars (sem hex) | Auditado em jun/2026 no CODEBASE | `public/css/dashboard.css` + Chart.js via vars |

#### 4.2 KPI comparison

**Advocacia (`painel/kpis.py` → chaves principais):**

- `total_clientes`, `servicos_ativos`
- `parcelas_vencidas`, `parcelas_a_vencer_30d`, `recebido_mes`, `recebido_periodo`, `recebido_hoje`, `previsto_mes`
- `audiencias_hoje`, `audiencias_amanha`, `audiencias_semana`
- `prazos_urgentes`, `prazos_vencidos`, `prazos_criticos`
- `tarefas_pendentes`, `tarefas_atrasadas`
- `honorarios_ativos`, `custas_abertas`, `taxa_recebimento`

**Engenharia (`dashboard/kpis.py` → chaves principais):**

- `active_projects`, `total_customers`
- `urgent_deadlines`, `overdue_deadlines`
- `open_tasks`, `late_tasks`
- `permits_today`, `permits_tomorrow`
- Financeiro (Manager only): `amount_overdue`, `amount_receivable`, `amount_received_month`, `contract_pipeline`, `spec_project_total`, margens

**Engenharia exclusivo no payload:** `centro_atencao`, `atencao`, `saude_operacional`, `agenda`, `commissions` — tiles operacionais ausentes no painel advocacia.

---

### 5. Calendar sync

| | Advocacia (`calendar_sync.py`) | Engenharia (`calendar_sync.py`) |
| --- | --- | --- |
| Origem | `Hearing`, `Deadline` | `Deadline`, `Permit` |
| Destino | `Event` + `custom_source_*` | Idem |
| Cancelamento | Status cancelado/concluído → cancela Event | Idem |
| Hooks | `doc_events` em `hooks.py` (4 entradas) | 4 entradas |
| Testes | `tests/test_calendar_sync.py` (6 métodos) | Idem (6 métodos) |

Paridade estrutural — domínios diferentes, implementação equivalente.

---

### 6. Testes

| Métrica | Advocacia | Engenharia |
| --- | ---: | ---: |
| Arquivos `test*.py` | 34 | 39 |
| Métodos `test_*` | 222 | 192 |
| Execução site `advocacia.local` | ✅ OK | ❌ app não instalado |
| Testes de permissão | ❌ | ✅ `test_permissions.py` (7) |
| Testes dashboard/painel | ✅ `test_painel_api.py` (9) | ✅ `test_dashboard.py` (10) |
| Testes IA | ❌ | ✅ `test_agent_api.py` (6) |
| Stubs vazios (`pass` / `...`) | 0 encontrados | 0 encontrados |

**Cobertura destacada advocacia:** validators (16), registro_horas (15), cliente (13), scheduler (9), financeiro (7), calendar_sync (6).

---

### 7. Connections / Links

#### Hub advocacia — `Legal Case`

Links de saída: `cliente`, `fase_processual`, `vara`, `tribunal`, `comarca`

Satélites com `servico`:

- Fee Agreement
- Hearing
- Case Communication
- Deadline
- Court Cost
- Legal Payment
- Service Record
- Time Entry
- Legal Task

#### Hub engenharia — `Construction Project`

Links de saída: `customer`

Satélites com `project` (13): Commission, Communication Log, Construction Measurement, Deadline, Engineering Contract, Payment, Permit, Project Item, Project Stage, Reimbursable Expense, Task, Time Log, Work Cost

**Office Expense** (advocacia) e cadastros jurídicos (Jurisdiction, Court Branch, Court) não orbitam `Legal Case` — equivalente intencional a cadastros globais / fluxos paralelos.

---

### 8. Field descriptions

| App | Com description | Total campos | % |
| --- | ---: | ---: | ---: |
| Advocacia | 12 | 232 | 5,2% |
| Engenharia | 346 | 352 | 98,3% |

Engenharia mantém dicionário central em `engenharia/scripts/add_field_descriptions.py` (518 linhas) aplicável via script de manutenção. Advocacia não possui equivalente.

---

### 9. Hooks e scheduler

#### doc_events (sem duplicatas por DocType+evento)

**Advocacia:**

| DocType | Eventos |
| --- | --- |
| Fee Agreement | on_update |
| Fee Installment | on_update |
| Legal Payment | on_update, on_trash |
| Hearing | after_insert, on_update |
| Deadline | after_insert, on_update |

**Engenharia:**

| DocType | Eventos |
| --- | --- |
| Engineering Contract | on_update |
| Reimbursable Expense | on_update |
| Engineering Contract Installment | on_update |
| Payment | on_update, on_trash |
| Deadline | after_insert, on_update |
| Permit | after_insert, on_update |
| Project Stage | on_update |

#### scheduler_events

| | Advocacia | Engenharia |
| --- | --- | --- |
| daily | 5 jobs (parcelas, despesas, notificações audiência/prazo) | 1 job (`check_overdue_installments`) |
| weekly | 1 (`verificar_status_servicos`) | — |

#### `frappe.db.commit()` fora de setup/patches

| App | Locais |
| --- | --- |
| Advocacia | `setup/*`, `patches/*`, `titulos.backfill_titulos_vazios` |
| Engenharia | `setup/*`, `patches/*`, `commands.py` (seed-demo) |

Nenhum `commit()` em schedulers/tasks/APIs em ambos — conforme disciplina §9.

---

### 10. Geração de documentos

| | Advocacia | Engenharia |
| --- | --- | --- |
| Módulo | `documentos.py` (601 linhas) | `documents.py` (492 linhas) |
| Engine | docxtpl | docxtpl |
| Whitelist | 4 endpoints; todos com `has_permission` | 4 endpoints; todos com `has_permission` |
| DocTypes | Document Template, Document Kit | Document Template, Document Kit |
| Testes | `test_documentos.py`, `test_document_kit.py` | `test_documents.py`, `test_document_kit.py` |

Engenharia adiciona placeholders de obra (specs, contrato, customer). Advocacia cobre placeholders jurídicos (serviço, cliente, processo).

---

### 11. Navegação (FAB + Header)

| Recurso | Advocacia | Engenharia |
| --- | --- | --- |
| `list_nav.js` | ✅ `public/js/list_nav.js` — filtros de lista a partir do painel | ❌ ausente |
| Integração painel | `advocacia.list_nav.goto(doctype, filters)` em `painel.js` | Navegação via módulos dashboard (`lists.js`, `filters.js`) |
| Ações rápidas (FAB) | Botões inline no `painel.js` / header hero | `public/js/dashboard/quick_actions.js` — chips `frappe.new_doc` |
| Header hero | `render_header()` em `painel.js` | `public/js/dashboard/hero.js` |
| `app_include_js` | masks, list_nav, cliente_from_servico, timer_global | masks, timer_global |

**Divergência:** engenharia modularizou UX do dashboard mas perdeu `list_nav`; advocacia mantém navegação filtrada lista↔painel no monolito.

---

### 12. Demo data seeder

| | Advocacia | Engenharia |
| --- | --- | --- |
| Módulo | `setup/seed_demo.py` (~595 linhas) | `setup/demo_data.py` (~1340 linhas) |
| Produção | Explicitamente dev-only (comentário no topo) | `DEMO_MARKER = "_DEMO_"` + teardown |
| Comando bench | ❌ | ✅ `bench seed-demo --site X` / `clear-demo` |
| Registro | — | `engenharia/commands.py` |
| Testes | Usado indiretamente via factories | `test_seed.py` |

---

### 13. AI readiness

| | Engenharia | Advocacia |
| --- | --- | --- |
| `agent_api.py` | ✅ 3 endpoints read-only agregados | ❌ |
| Endpoints | `get_active_projects`, `get_project_summary`, `get_costs_by_category` | — |
| Permissões | `has_permission` + strip financeiro para User | — |
| Documentação | `docs/audit_ai_readiness.md` | — |
| Testes | `test_agent_api.py` | — |

Equivalente jurídico sugerido: `get_active_servicos`, `get_servico_summary` (honorários/prazos/audiências; financeiro só Manager).

---

## 3. Plano de ação priorizado

### Quick wins (<1h cada)

1. **Documentar** no `CODEBASE.md` ou README que `ENGENHARIA_STANDARDS.md` não governa advocacia.
2. **Adicionar `has_permission` na facade** `painel_api.py` (espelhar `dashboard_api.py`).
3. **Type hints** nos 2 endpoints de `painel_api.py` (baixo risco, alto alinhamento).
4. **Registrar comando** `bench seed-demo` no advocacia (wrapper sobre `seed_demo.py` existente).
5. **Confirmar** ausência de deprecations (`cur_frm`, etc.) — já OK; incluir no checklist pré-release.

### Médio (1–4h cada)

1. **Field descriptions:** adaptar `add_field_descriptions.py` para DocTypes PT (priorizar Legal Case, Client, Legal Payment, Acordo).
2. **Whitelist gaps:** `has_permission` em parcelas, tarefa, timers; type hints nos whitelists de `financeiro.py` e `documentos.py`.
3. **KPI tiles:** portar `attention.py` / `health.py` do engenharia como `centro_atencao` enriquecido no painel (sem mudar domínio jurídico).
4. **`test_permissions.py`:** validar Advocacia User vs Manager em Legal Payment e painel.
5. **Sincronizar navegação:** decidir se engenharia ganha `list_nav.js` ou advocacia migra para padrão `quick_actions` — documentar decisão.
6. **`REGRAS_ADVOCACIA.md`:** extrair de CODEBASE + auditorias as regras fechadas (PT congelado, um handler/doc_event, etc.).

### Longo (1+ dia)

1. **Modularizar `painel.js`:** extrair para `public/js/painel/` (kpis, financeiro, timeline, hero, list_nav) — espelhar engenharia.
2. **`setup/permissions.py`:** Custom DocPerm Manager/User; permlevel em campos financeiros de Acordo/Legal Payment; filtrar payload financeiro do painel.
3. **`agent_api.py` jurídico:** endpoints agregados + testes + doc de audit IA.
4. **Dashboard role parity completa:** ocultar valores de honorários/custas para Advocacia User em backend **e** frontend.

---

## 4. O que NÃO replicar (engenharia → advocacia)

Estes itens são **específicos de domínio de obra** ou decisões greenfield — não aplicar ao advocacia brownfield:

| Feature engenharia | Motivo para não replicar |
| --- | --- |
| DocTypes / fieldnames em inglês | Advocacia PT congelado por compatibilidade de dados e UX |
| `Construction Project`, `Work Cost`, `Permit`, `Commission`, `Project Item`, `Construction Measurement` | Domínio civil; equivalentes jurídicos já existem |
| `Project Stage` + Kanban "Engenharia Obras" | Gestão de etapa física de obra — usar `Case Phase` / Legal Task |
| `Reimbursable Expense` vs `Work Cost` split | Modelo financeiro de obra; advocacia usa Despesa/Custa/Atos |
| `Contract Amendment` + botão "Aplicar Aditivo" | Aditivo de contrato de **obra** — honorários usam Acordo + parcelas |
| `agent_api.get_costs_by_category` | Agregação de custo por fornecedor/categoria de obra |
| `project_rollup.py` / `project_progress.py` | Rollup de specs, medições, avanço físico |
| `importable_doctypes` | Export/import CSV de obras — sem equivalente jurídico definido |
| Print Format fixtures (Contrato de Obra, Orçamento) | Templates jurídicos já em Document Template |
| `Technical Item` / EAV de especificações | Placeholders técnicos de engenharia (ART, área, etc.) |
| Renomear `Legal Case` → hub EN | Quebra URLs, reports, fixtures e dados existentes |
| Política "um DocType por commit" retroativa | Brownfield — aplicar só a **novos** DocTypes |
| `setup/seed.py` idempotente em produção | Advocacia já tem seed_demo dev-only — manter separação |

---

## Referências de arquivos

| Tópico | Advocacia | Engenharia |
| --- | --- | --- |
| Norma / inventário | `CODEBASE.md` | `REGRAS_OBRIGATORIAS.md` |
| Títulos | `advocacia/titulos.py` | `engenharia/titles.py` |
| Dashboard backend | `advocacia/painel/` | `engenharia/dashboard/` |
| Dashboard facade | `advocacia/painel_api.py` | `engenharia/dashboard_api.py` |
| Dashboard frontend | `page/painel/painel.js` | `page/eng_dashboard/` + `public/js/dashboard/` |
| Calendar | `advocacia/calendar_sync.py` | `engenharia/calendar_sync.py` |
| Documentos | `advocacia/documentos.py` | `engenharia/documents.py` |
| Permissões | `setup/install.py` (roles only) | `setup/permissions.py`, `setup/roles.py` |
| Demo | `setup/seed_demo.py` | `setup/demo_data.py`, `commands.py` |
| IA | — | `agent_api.py` |
| Descriptions | — | `scripts/add_field_descriptions.py` |
| Navegação lista | `public/js/list_nav.js` | — |

---

*Relatório gerado por inspeção estática do código em 2026-06-06. Revisar após mudanças estruturais em qualquer app.*
