# CODEBASE — App Advocacia (Frappe v16)

> Documento gerado por auditoria completa do repositório em 2026-05-31.  
> **Não** derivado de CODEBASE.md / CODEBASE_FINAL.md anteriores — reflete o estado real dos arquivos lidos.

---

## 1. VISÃO GERAL

| Item | Valor |
|------|-------|
| **Nome do app** | advocacia |
| **Versão (pyproject.toml)** | 0.6.0 |
| **Framework** | Frappe v16 (bench local: v16.19.0) |
| **Licença** | MIT (`license.txt`, `app_license = "mit"`) |
| **Publisher** | Charles Tomazini |
| **Módulo Frappe** | Advocacia (`modules.txt`) |
| **Branch Git** | `frappe-v16` |
| **Remote** | `git@github.com:ctomazini/advocacia.git` |

**Propósito:** LegalTech para escritório de advocacia brasileiro — gestão de clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas, painel operacional e geração de documentos (.docx).

**Sites:**
- **Dev (documentado em `.cursorrules`):** `advocacia.local` (porta 8000), bench `/home/frappe/frappe-bench`
- **Produção:** não documentado no repositório

**Métricas do repositório (excl. `.git`, `__pycache__`, `node_modules`):**

| Tipo | Linhas totais |
|------|---------------|
| Python (`.py`) | 7.919 |
| JavaScript (`.js`) | 6.821 |
| JSON (`.json`) | 13.192 |
| Arquivos rastreados | ~149 |

**Dependências externas:**

| Fonte | Dependência |
|-------|-------------|
| `pyproject.toml` | `docxtpl>=0.18.0` (geração .docx) |
| `pyproject.toml` | Python `>=3.10` (README recomenda 3.12+) |
| Frappe Bench | `frappe` v16.x, MariaDB 10.6+ |
| Build assets | Node.js 20+ (README: ≥24 recomendado para `bench build`) |
| Runtime JS | `jquery.inputmask` (via Frappe, usado em `masks.js`) |
| `requirements.txt` | **não encontrado** |
| `package.json` | **não encontrado** (assets via Frappe build) |

**Frappe compatível:** v16.x (desenvolvido/testado em v16.19.0).

---

## 2. ÁRVORE DE ARQUIVOS

```
advocacia/                              # Raiz do repositório Git
├── CODEBASE.md                         # Este documento
├── CODEBASE_FINAL.md                   # Doc legado (desatualizado — ver seção 11)
├── README.md                           # Instalação, testes (contagem desatualizada)
├── pyproject.toml                      # Metadados app v0.6.0, dependência docxtpl
├── license.txt                         # MIT
├── .cursorrules                        # Regras de arquitetura para agentes
├── .pre-commit-config.yaml             # Hooks pre-commit
├── .eslintrc / .editorconfig / .gitignore
│
└── advocacia/                          # Pacote Frappe app
    ├── hooks.py                        # Fixtures, scheduler, doc_events, after_migrate
    ├── modules.txt                     # Módulo "Advocacia"
    ├── patches.txt                     # Patches v16_0 pós-migrate
    ├── patches/v16_0/                  # Migrações Pagamento (3 scripts)
    │
    ├── fixtures/
    │   ├── workspace.json              # Workspace Advocacia exportado
    │   ├── notification.json           # 2 Notifications nativas
    │   └── custom_field.json           # Custom Fields em Event (calendar sync)
    │
    ├── workspace_sidebar/
    │   └── advocacia.json              # Sidebar canônica (26 links)
    │
    ├── desktop_icon/
    │   └── advocacia.json              # Ícone app → Workspace Sidebar Advocacia
    │
    ├── public/js/                      # JS global (app_include_js)
    │   ├── masks.js                    # Máscaras CPF/CNPJ/CNJ/telefone/CEP
    │   ├── list_nav.js                 # Navegação programática para List View filtrada
    │   ├── navegacao.js                # FAB + botão header → Painel
    │   ├── servico_link.js             # Formatter Link Servico
    │   ├── cliente_from_servico.js     # Auto-fill cliente a partir de servico
    │   └── timer_global.js             # Widget timer global Registro de Horas
    │
    └── advocacia/                      # Módulo Python Advocacia
        ├── validators.py               # CPF, CNPJ, CNJ, telefone, email (Receita/CNJ/ANATEL)
        ├── painel_api.py               # API whitelisted do Painel (~900+ linhas)
        ├── documentos.py               # Gerador docx v2, kits, placeholders
        ├── financeiro.py               # Sync Pagamento↔Parcela↔Acordo↔Atos
        ├── tasks.py                    # Schedulers daily/weekly
        ├── notificacoes.py             # Email digest prazos (daily)
        ├── calendar_sync.py            # Sync Audiencia/Prazo → Event nativo
        │
        ├── setup/
        │   ├── __init__.py             # reinstalar_istable_doctypes
        │   ├── install.py              # after_install, Custom Fields Event
        │   ├── sidebar.py              # ensure_advocacia_sidebar (import JSON)
        │   ├── workspace.py            # ensure_advocacia_workspace
        │   ├── reports.py              # ensure_advocacia_reports
        │   └── translations.py         # Traduções PT de nomes DocType
        │
        ├── tests/                      # 20 módulos, 167 testes (ver seção 11)
        │
        ├── doctype/                    # 24 DocTypes (19 document + 5 child)
        │   ├── servico/                # Hub central processo/consultoria
        │   ├── cliente/                # Cliente PF/PJ + child contato/endereço
        │   ├── acordo_de_honorarios_processuais/
        │   ├── parcela_de_honorarios/  # istable
        │   ├── pagamento/              # Hub financeiro unificado
        │   ├── registro_de_atos/ + ato_advocaticio/
        │   ├── audiencia/ + controle_de_prazos/
        │   ├── tarefa/ + comunicacao/
        │   ├── registro_de_horas/
        │   ├── custa_processual/ + despesa_do_escritorio/
        │   ├── template_documento/ + kit_de_documentos/ + kit_documento_item/
        │   ├── configuracao_do_escritorio/  # Single
        │   └── comarca/ vara/ tribunal/ fase_processual/  # Auxiliares
        │
        ├── page/painel/                # Page custom painel.js + painel.json
        │
        ├── report/                     # 6 Script Reports
        │   ├── produtividade/
        │   ├── horas_por_servico/
        │   ├── inadimplencia/
        │   ├── fluxo_de_caixa/
        │   ├── honorarios_por_cliente/
        │   └── carteira_ativa/
        │
        └── workspace/advocacia/
            └── advocacia.json          # Workspace JSON canônico
```

---

## 3. MAPA DE DOCTYPES

**Total:** 24 DocTypes (`custom=0` em todos). **19** documentos standalone + **5** child tables + **1** Single.

Legenda colunas: `reqd`/`unique`/`hidden`/`default` vazios = ausente ou 0 no JSON.

### 3.1 Configuracao do Escritorio (Single)

| Campo | Valor |
|-------|-------|
| **Nome** | Configuracao do Escritorio |
| **Module** | Advocacia |
| **custom** | 0 |
| **autoname** | — |
| **is_submittable** | — |
| **istable** | — |
| **issingle** | 1 |
| **title_field** | — |
| **search_fields** | — |

| fieldname | label | fieldtype | options | reqd | unique | hidden | default |
|-----------|-------|-----------|---------|------|--------|--------|---------|
| sec_identificacao | Identificação | Section Break | | | | | |
| razao_social | Razão Social | Data | | 1 | | | |
| cnpj | CNPJ | Data | | | | | |
| registro_sia | Registro SIA | Data | | | | | |
| column_break_1 | | Column Break | | | | | |
| advogada | Advogada(o) Principal | Data | | 1 | | | |
| oab | OAB | Data | | 1 | | | |
| sec_endereco | Endereço Profissional | Section Break | | | | | |
| endereco | Endereço Completo | Small Text | | 1 | | | |

**Permissions:** Advocacia Manager (full), Advocacia User (read-only), System Manager (full)  
**Links:** —  
**Child Tables:** —

---

### 3.2 Kit de Documentos

| Campo | Valor |
|-------|-------|
| **Nome** | Kit de Documentos |
| **autoname** | field:titulo |
| **naming_rule** | By fieldname |
| **title_field** | titulo |
| **search_fields** | titulo,descricao |

| fieldname | label | fieldtype | options | reqd | unique | hidden | default |
|-----------|-------|-----------|---------|------|--------|--------|---------|
| titulo | Título | Data | | 1 | 1 | | |
| descricao | Descrição | Small Text | | | | | |
| column_break_1 | | Column Break | | | | | |
| habilitado | Habilitado | Check | | | | | 1 |
| templates_section | Templates | Section Break | | | | | |
| templates | Templates | Table | Kit Documento Item | 1 | | | |

**Permissions:** Advocacia Manager, Advocacia User, System Manager  
**Links:** —  
**Child Tables:** templates → Kit Documento Item

---

### 3.3 Kit Documento Item (istable=1)

| fieldname | label | fieldtype | options | reqd | unique | hidden | default |
|-----------|-------|-----------|---------|------|--------|--------|---------|
| template | Template | Link | Template Documento | 1 | | | |
| ordem | Ordem | Int | | | | | 0 |

**Permissions:** `[]` (child)  
**Links:** template → Template Documento

---

### 3.4 Template Documento

| fieldname | label | fieldtype | options | reqd | unique | hidden | default |
|-----------|-------|-----------|---------|------|--------|--------|---------|
| titulo | Título | Data | | 1 | 1 | | |
| tipo_documento | Tipo de Documento | Select | (opções fixas) | | | | |
| descricao | Descrição | Small Text | | | | | |
| column_break_1 | | Column Break | | | | | |
| habilitado | Habilitado | Check | | | | | 1 |
| arquivo | Arquivo .docx | Attach | | 1 | | | |
| section_break_2 | Referência | Section Break | | | | | |
| ver_placeholders | Ver Placeholders | Button | | | | | |

**autoname:** field:titulo | **title_field:** titulo | **search_fields:** titulo,tipo_documento

---

### 3.5 Servico

| Campo | Valor |
|-------|-------|
| **autoname** | format:SERV-{####} |
| **naming_rule** | Expression (old style) |
| **title_field** | title |
| **search_fields** | title,cliente,numero_processo,status |

| fieldname | label | fieldtype | options | reqd |
|-----------|-------|-----------|---------|------|
| cliente | Cliente | Link | Cliente | 1 |
| tipo | Tipo | Select | Processo Judicial/Consultoria/... | 1 |
| title | Título | Data | | |
| status | Status | Select | Em andamento/Encerrado/Suspenso/Arquivado | |
| fase_processual | Fase Processual | Link | Fase Processual | |
| data_abertura | Data de Abertura | Date | | |
| numero_processo | Número do Processo | Data | | |
| numeracao_legada | Numeração legada | Check | | |
| area | Área | Select | Família/Trabalhista/Cível/... | |
| vara | Vara | Link | Vara | |
| tribunal | Tribunal | Link | Tribunal | |
| comarca | Comarca | Link | Comarca | |
| parte_contraria | Parte Contrária | Data | | |
| valor_causa | Valor da Causa | Currency | | |
| observacoes | Observações | Text Editor | | |

**Links:** cliente, fase_processual, vara, tribunal, comarca  
**Controller:** validação CNJ (`validators.py`), compose title, `servico_query`, `get_link_title`

---

### 3.6 Cliente

| fieldname | label | fieldtype | options | reqd | unique |
|-----------|-------|-----------|---------|------|--------|
| tipo_pessoa | Tipo de Pessoa | Select | PF/PJ | 1 | |
| nome | Nome / Razão Social | Data | | 1 | |
| cpf | CPF | Data | | | 1 |
| cnpj | CNPJ | Data | | | 1 |
| contatos | Contatos | Table | Contato Cliente | | |
| enderecos | Endereços | Table | Endereco Cliente | | |

**autoname:** format:CLI-{####} | **title_field:** nome | **search_fields:** nome,cpf,cnpj  
**Controller:** CPF/CNPJ/telefone/email validation, limpeza dígitos

---

### 3.7 Contato Cliente (istable=1)

| fieldname | fieldtype | options | reqd |
|-----------|-----------|---------|------|
| nome | Data | | 1 |
| tipo | Select | Principal/Conjuge/... | |
| telefone | Data | | |
| celular | Data | | |
| email | Data | Email | |
| observacao | Small Text | | |

---

### 3.8 Endereco Cliente (istable=1)

| fieldname | fieldtype |
|-----------|-----------|
| tipo, cep, logradouro, numero, complemento, bairro, cidade, estado, principal | Data/Check |

---

### 3.9 Acordo de Honorarios Processuais

| Campo | Valor |
|-------|-------|
| **autoname** | format:ACOR-{####} |
| **title_field** | servico (Link — exibe ID) |
| **search_fields** | servico,cliente,status,tipo_de_cobrança |

Campos principais: servico, cliente, modo_honorarios, status, valores (percentual/fixo/misto), sucumbência, parcelamento, **table_ztjx** → Parcela de Honorarios, totais, observações.

**Links:** servico, cliente  
**Child Tables:** table_ztjx → Parcela de Honorarios

---

### 3.10 Parcela de Honorarios (istable=1)

| fieldname | fieldtype | options |
|-----------|-----------|---------|
| vencimento | Date | |
| valor_total, valor_advogada, valor_sucumbência, valor_cliente | Currency | |
| descrição | Small Text | |
| parcela_origem_id | Data | hidden=1 |
| pagamento | Link | Pagamento |
| status | Select | Pendente/Vencida/Recebida/Repassada/Cancelada |
| data_recebimento, data_repasse | Date | |
| forma_recebimento | Select | PIX/TED/... |
| observacao | Small Text | |

---

### 3.11 Pagamento

| Campo | Valor |
|-------|-------|
| **autoname** | naming_series: |
| **title_field** | descricao |
| **search_fields** | servico,cliente,status,data_vencimento |

Campos: naming_series, servico, cliente, tipo_origem, acordo, registro_atos, numero_parcela, descricao, parcela_origem_id, sincronizado_em, manual_override, valor, valor_recebido, data_vencimento, data_recebimento, status, observacoes, comprovante.

**Links:** servico, cliente, acordo, registro_atos  
**Status:** Pendente, Vencido, Recebido, Cancelado, Renegociado, Repassado

---

### 3.12 Registro de Atos + Ato Advocaticio

**Registro de Atos:** servico, cliente, status, data_abertura, **atos** (Table Ato Advocaticio), totais, cobrança, ultimo_pagamento→Pagamento, gerar_cobranca (Button).

**Ato Advocaticio (istable):** data, tipo, descrição, valor, status, **cobranca_id** (fieldtype **Data**, label "Pagamento" — inconsistência).

---

### 3.13 Audiencia

| fieldname | fieldtype | options |
|-----------|-----------|---------|
| servico, cliente | Link | Servico, Cliente |
| data_hora | Datetime | |
| status_aud | Select | |
| tipo | Select | |
| modalidade | Select | Presencial/Virtual (sem Híbrida) |
| link_virtual | Data | URL |
| local_vara | Link | Vara |
| resultado | Select | |
| observacoes | Text Editor | |

**autoname:** format:AUD-{####} | **title_field:** tipo

---

### 3.14 Controle de Prazos

servico, cliente, data_prazo, status, descricao, prioridade, responsavel→User, dias_notificacao (default 3), observacoes.

**autoname:** format:PRAZO-{####} | **title_field:** descricao

---

### 3.15 Tarefa

servico, cliente, titulo, status, prioridade, data_limite, descricao, responsavel→User, data_conclusao, naming_series (hidden).

**autoname:** naming_series: | **title_field:** titulo

---

### 3.16 Comunicacao

servico, cliente, data, tipo, assunto, resumo, proximos_passos, gerar_tarefa, tarefa→Tarefa.

**autoname:** format:COM-{YYYY}-{####} | **title_field:** assunto

---

### 3.17 Registro de Horas

servico, cliente, data, responsavel, hora_inicio/fim, duracao_minutos/horas, atividade, categoria, descricao, cobravel, timer_display, timer_inicio, timer_ativo.

**autoname:** format:HRS-{YYYY}-{####} | **title_field:** atividade

---

### 3.18 Custa Processual

servico, cliente, tipo, descricao, status, valor, datas, repassar_cliente, forma_pagamento, comprovante, observacoes.

**autoname:** format:CUST-{YYYY}-{####}

---

### 3.19 Despesa do Escritorio

descricao, categoria, valor, status, data_vencimento, data_pagamento, forma_pagamento, recorrente, frequencia, proximo_vencimento, comprovante, observacoes.

**autoname:** format:DESP-{YYYY}-{####}

---

### 3.20 Comarca (auxiliar)

| fieldname | fieldtype | reqd | unique |
|-----------|-----------|------|--------|
| comarca_name | Data | 1 | 1 |
| uf | Select (27 UFs) | 1 | |
| city | Data | | |

**autoname:** field:comarca_name

---

### 3.21 Vara (auxiliar)

vara_name (unique), comarca→Comarca, court_type (Select tipos vara).

**autoname:** field:vara_name

---

### 3.22 Tribunal (auxiliar)

tribunal_name, abbreviation (unique), jurisdiction (Esfera + Eleitoral).

**autoname:** field:tribunal_name

---

### 3.23 Fase Processual (auxiliar)

phase_name (unique), sort_order (Int).

**autoname:** field:phase_name

---

### 3.24 Grafo de Links (app-only)

```
Cliente ← Servico, Pagamento, Tarefa, Comunicacao, Registro de Horas, Custa Processual,
          Registro de Atos, Acordo, Controle de Prazos, Audiencia
Comarca ← Vara, Servico | Vara ← Servico, Audiencia
Template Documento ← Kit Documento Item
Pagamento ← Parcela de Honorarios, Registro de Atos
Tarefa ← Comunicacao
```

---

## 4. HOOKS.PY — Mapa Completo

**Arquivo:** `advocacia/hooks.py`

### fixtures

| DocType exportado | Filtro |
|-------------------|--------|
| Workspace | name = Advocacia |
| Notification | name IN (Advocacia - Prazo vencendo, Advocacia - Audiencia amanha) |
| Custom Field | dt=Event, fieldname LIKE custom_source% |

### app_include_js

| Asset | Função |
|-------|--------|
| masks.js | Máscaras CPF/CNPJ/CNJ/telefone/CEP via jquery.inputmask |
| list_nav.js | `advocacia.list_nav.goto(doctype, filters)` |
| navegacao.js | FAB + botão header → rota `painel` |
| servico_link.js | Formatter customizado Link Servico |
| cliente_from_servico.js | Preenche cliente ao selecionar servico (Quick Entry + forms) |
| timer_global.js | Widget timer ativo Registro de Horas |

### standard_queries

| DocType | Handler |
|---------|---------|
| Servico | `advocacia.advocacia.doctype.servico.servico.servico_query` |

### override_whitelisted_methods

| Método nativo | Override |
|---------------|----------|
| frappe.desk.search.get_link_title | `advocacia.advocacia.doctype.servico.servico.get_link_title` |

### scheduler_events

| Frequência | Função | Propósito |
|------------|--------|-----------|
| daily | tasks.verificar_parcelas_vencidas | Pagamento/Parcela vencidos → status Vencido/Vencida |
| daily | tasks.verificar_despesas_vencidas | Despesa Pendente vencida → Atrasado |
| daily | tasks.notificar_parcelas_vencidas | Notificação sistema Pagamento Vencido há 3 dias |
| daily | tasks.notificar_audiencias_hoje | Notificação audiências do dia |
| daily | notificacoes.notificar_prazos_diario | Email HTML digest prazos para Advocacia Manager |
| weekly | tasks.verificar_status_servicos | Auto-arquiva Servico inativo 90+ dias |

### doc_events

| DocType | Evento | Handler |
|---------|--------|---------|
| Acordo de Honorarios Processuais | on_update | financeiro.sincronizar_pagamentos_hook |
| Parcela de Honorarios | on_update | tasks.on_parcela_update |
| Pagamento | on_update | tasks.on_pagamento_update + financeiro.on_pagamento_update_honorarios |
| Pagamento | on_trash | financeiro.on_pagamento_trash |
| Audiencia | after_insert, on_update | calendar_sync.sync_audiencia_to_event |
| Controle de Prazos | after_insert, on_update | calendar_sync.sync_prazo_to_event |

### after_install

`advocacia.advocacia.setup.install.after_install` — roles, permissões iniciais

### after_migrate (ordem)

1. `setup.reinstalar_istable_doctypes` — reimporta child tables órfãs
2. `setup.install.after_install`
3. `setup.install.ensure_event_custom_fields`
4. `setup.translations.ensure_doctype_translations`
5. `setup.sidebar.ensure_advocacia_sidebar`
6. `setup.reports.ensure_advocacia_reports`
7. `setup.workspace.ensure_advocacia_workspace`

**Verificação hooks ↔ código:** todos os 22 paths referenciados existem e são importáveis ✅

---

## 5. FUNÇÕES WHITELISTED (API PÚBLICA)

| Função (path completo) | Parâmetros | Retorno | Permissão | Chamado por |
|------------------------|------------|---------|-----------|-------------|
| painel_api.get_painel_data | limit_start, limit_page_length, periodo_dias, list_limit, list_limits | dict KPIs/listas | Servico read | painel.js xcall |
| painel_api.marcar_parcela_recebida | parcela_name | {ok, name, parent} | Pagamento write | painel.js, pagamento.js |
| documentos.gerar_documento | servico_name, template_name | {file_url, file_name} | Servico read (indireto) | testes only |
| documentos.gerar_documentos_em_lote | servico_name, template_names | {success, data} | Servico read | servico.js |
| documentos.get_templates_disponiveis | — | list | Template Documento read | servico.js |
| documentos.get_kits_disponiveis | — | list kits | Kit de Documentos read | servico.js |
| documentos.get_placeholders_referencia | — | dict | **nenhuma** | template_documento.js |
| documentos.get_placeholders_disponiveis | — | dict legacy | **nenhuma** | testes only (dead UI) |
| financeiro.resync_pagamentos_acordo | acordo_name | {status: ok} | Acordo write | acordo.js |
| financeiro.bulk_delete_pagamentos | names | {excluidos, ignorados} | Pagamento delete | pagamento_list.js |
| financeiro.gerar_pagamento_atos | registro_name, data_vencimento | sync result | Registro de Atos write | testes |
| financeiro.sincronizar_pagamento_atos | registro_name, data_vencimento | sync result | Registro de Atos write | registro_de_atos.js |
| financeiro.cancelar_cobranca_pagamento_atos | pagamento_name | result | Pagamento write | pagamento.js |
| financeiro.cancelar_pagamento_honorarios | pagamento_name | result | Pagamento write | pagamento.js |
| servico.servico_query | search args | [(name,label)] | @validate_and_sanitize_search_inputs | Link field |
| servico.get_link_title | doctype, docname | string | **nenhuma** | Frappe desk global |
| registro_de_horas.iniciar_timer | doc method | {timer_inicio} | **nenhuma** + ignore_permissions save | registro_de_horas.js |
| registro_de_horas.parar_timer | doc method | duracao | **nenhuma** + ignore_permissions | registro_de_horas.js |
| registro_de_horas.get_timer_ativo_usuario | — | timer dict | Registro de Horas read | timer_global.js |
| audiencia.get_events | start, end, filters | events[] | Audiencia read | audiencia_calendar.js |
| controle_de_prazos.get_events | idem | events[] | Controle de Prazos read | controle_de_prazos_calendar.js |
| despesa_do_escritorio.gerar_proxima_despesa | source_name | new name | **nenhuma** + ignore_permissions insert | despesa.js |
| parcela_de_honorarios.registrar_recebimento | doc method | {status} | doc perms | parcela.js |
| parcela_de_honorarios.registrar_repasse | doc method | {status} | doc perms | parcela.js |
| tarefa.concluir | doc method | {status} | doc perms | tarefa.js |

---

## 6. SERVER SCRIPTS / SCHEDULED TASKS

| Arquivo | Função | Frequência | Queries / lógica |
|---------|--------|------------|------------------|
| tasks.py | verificar_parcelas_vencidas | daily | get_all Pagamento/Parcela vencidos; db.set_value |
| tasks.py | verificar_despesas_vencidas | daily | get_all Despesa Pendente vencida |
| tasks.py | notificar_parcelas_vencidas | daily | Pagamento Vencido exatamente -3 dias; Notification |
| tasks.py | notificar_audiencias_hoje | daily | Audiencia hoje; Notification owner |
| tasks.py | verificar_status_servicos | weekly | Servico Em andamento sem atividade → Arquivado; N+1 db.count |
| notificacoes.py | notificar_prazos_diario | daily | get_all prazos pendentes (sem limit); sendmail HTML |
| financeiro.py | sincronizar_pagamentos_hook | doc_event | Sync parcelas ↔ Pagamento |
| calendar_sync.py | sync_*_to_event | doc_event | insert/save Event ignore_permissions |

**SQL raw (frappe.db.sql):**

| Arquivo | Linhas | Uso |
|---------|--------|-----|
| painel_api.py | 691, 723, 814, 831 | SUM despesas/custas/horas (parametrizado) |
| patches/v16_0/preencher_tipo_origem_pagamento.py | 8 | UPDATE tipo_origem |
| test_registro_horas.py | 115 | cleanup teste |

---

## 7. CLIENT-SIDE (JS)

### Global (`public/js/`)

| Arquivo | Escopo | Eventos / API |
|---------|--------|---------------|
| masks.js | Global AdvocaciaMasks | refresh masks CPF/CNPJ/CNJ/tel/CEP |
| list_nav.js | ListView patch | page-change, goto() |
| navegacao.js | FAB Painel | app_ready, router change |
| servico_link.js | Link formatter Servico | lê title, cliente, numero_processo |
| cliente_from_servico.js | 9 DocTypes | servico→cliente via db.get_value |
| timer_global.js | Widget fixo | xcall get_timer_ativo_usuario |

### DocType JS (principais)

| Arquivo | Botões / frappe.call |
|---------|---------------------|
| servico.js | Gerar Documentos bulk; get_templates/kits; gerar_documentos_em_lote |
| pagamento.js | Cancelar cobrança; marcar recebida; cancelar honorários |
| pagamento_list.js | bulk_delete_pagamentos |
| registro_de_atos.js | sincronizar_pagamento_atos |
| acordo.js | resync_pagamentos_acordo; gerar parcelas client-side |
| registro_de_horas.js | iniciar_timer, parar_timer |
| template_documento.js | get_placeholders_referencia |
| tarefa.js | concluir (doc method) |
| parcela.js | registrar_recebimento, registrar_repasse |
| despesa.js | gerar_proxima_despesa |
| audiencia.js | Entrar na Audiência (link_virtual) |
| *\_calendar.js | get_events calendar |

### Page painel.js

- `frappe.ui.make_app_page()` + CSS vars Frappe
- xcall get_painel_data, marcar_parcela_recebida
- KPIs, timeline, parcelas, despesas, custas, horas
- **Issue:** cores hex hardcoded no Chart.js (L2750–2753)

---

## 8. SETUP / MIGRATIONS

| Função | Arquivo | Propósito |
|--------|---------|-----------|
| after_install | install.py | Roles Advocacia User/Manager, permissões |
| ensure_event_custom_fields | install.py | Custom Fields Event para calendar_sync |
| ensure_doctype_translations | translations.py | Translation PT nomes DocType |
| ensure_advocacia_sidebar | sidebar.py | import workspace_sidebar + desktop_icon JSON |
| ensure_advocacia_workspace | workspace.py | import workspace/advocacia/advocacia.json |
| ensure_advocacia_reports | reports.py | Sync 6 Script Reports |
| reinstalar_istable_doctypes | setup/__init__.py | Reimporta child tables + Kit de Documentos se órfãos |

**Patches (patches.txt post_model_sync):**

- migrar_pagamentos.py — migra dados legado para Pagamento
- preencher_tipo_origem_pagamento.py — SQL UPDATE
- vincular_pagamento_parcelas.py — vincula parcelas existentes

---

## 9. RELATÓRIOS (REPORTS)

Todos **Script Report** (`report_type: "Script Report"`).

| Report | Colunas principais | Filtros | Lógica |
|--------|-------------------|---------|--------|
| produtividade | area, total_servicos, em_andamento, encerrados, taxa, horas, lucro | periodo, area, incluir_horas | GROUP Servico por area + joins |
| horas_por_servico | servico, cliente, total_horas, cobrável/não, valor_hora | servico, cliente | GROUP Registro de Horas |
| inadimplencia | cliente, total_vencido, qtd, dias_atraso, contato | cliente, de_data, ate_data | Pagamento Vencido GROUP cliente |
| fluxo_de_caixa | data, tipo, entrada/saída, saldo_acumulado | meses, cliente, incluir_despesas | Merge Pagamentos+Despesas+Custas |
| honorarios_por_cliente | totais contratado/recebido/pendente/vencido | cliente, datas, status | GROUP Pagamentos |
| carteira_ativa | servico, fase, proximo_prazo, audiencia, financeiro | cliente, area, tipo | Servicos ativos + subqueries |

**Testes:** produtividade e horas_por_servico têm testes; 4 reports sem testes dedicados.

---

## 10. FIXTURES E WORKSPACE

### Fixtures exportados (hooks)

- Workspace Advocacia
- 2 Notifications (prazo 3 dias antes, audiência 1 dia antes)
- Custom Fields Event: custom_source_doctype, custom_source_name

### Sidebar (`workspace_sidebar/advocacia.json`)

5 seções, **26 links**:

| Seção | Itens |
|-------|-------|
| Dia a Dia | Painel, Prazos, Audiências, Tarefas, Comunicações |
| Gestão de Casos | Serviços, Clientes, Registro de Horas, Registro de Atos, Custas |
| Financeiro | Pagamentos, Honorários, Despesas, Documentos, Kits de Documentos |
| Relatórios | 6 reports |
| Cadastros | Comarca, Vara, Tribunal, Fase Processual, Escritório |

Validação: `setup/sidebar.py` SIDEBAR_LINK_ORDER espelha JSON (26 entradas).

### Workspace JSON

- `links[]`: 22 links (faltam vs sidebar: Comunicacao, Registro de Horas, Custa, Despesa, 2 reports)
- `content` block: shortcuts órfãos **"Faturas"** e **"Cadastro de documentos"** sem entrada em shortcuts[]

---

## 11. TESTES

| Métrica | Valor |
|---------|-------|
| **Total testes** | **167** (`def test_*`) |
| README claim | 149 (**desatualizado**) |
| Módulos test_*.py | 20 (+ test_setup.py helpers, 0 testes) |

| Arquivo | Testes |
|---------|--------|
| test_validators.py | 16 |
| test_cliente.py | 13 |
| test_registro_horas.py | 12 |
| test_despesa_escritorio.py | 11 |
| test_acordo_honorarios.py | 10 |
| test_documentos.py | 9 |
| test_servico.py | 9 |
| test_scheduler.py | 9 |
| test_pagamento.py | 9 |
| test_painel_api.py | 8 |
| test_registro_atos.py | 8 |
| test_comunicacao.py | 7 |
| test_custa_processual.py | 7 |
| test_financeiro.py | 7 |
| test_audiencia.py | 6 |
| test_calendar_sync.py | 6 |
| test_controle_prazos.py | 6 |
| test_tarefa.py | 5 |
| test_notificacoes.py | 5 |
| test_report_produtividade.py | 4 |

**Stub fraco:** `test_scheduler.py::test_notificar_audiencias_amanha_nao_dispara` (L87–92) — termina com `pass`, sem assert.

**DocTypes sem teste dedicado:** Comarca, Vara, Tribunal, Fase Processual, Configuracao do Escritorio (CRUD), Kit de Documentos (só API list).

**Child tables sem teste direto:** Kit Documento Item.

---

## 12. INTEGRAÇÕES

| Integração | Status | Arquivo |
|------------|--------|---------|
| **Google Calendar** | Via Event nativo Frappe | calendar_sync.py + README setup OAuth |
| **Geração documentos** | docxtpl | documentos.py |
| **Notificações Frappe** | Notification DocType + enqueue_create_notification | tasks.py, fixtures |
| **Email digest prazos** | frappe.sendmail HTML | notificacoes.py |
| APIs externas (CNJ, Receita) | **não implementado** — validação local apenas | validators.py |

---

## 13. AUDITORIA DE QUALIDADE

### 13.1 Bugs e Erros Lógicos

| Sev | Arquivo:Linha | Problema |
|-----|---------------|----------|
| 🟠 | ato_advocaticio.json | `cobranca_id` fieldtype Data mas label "Pagamento" — não Link→Pagamento |
| 🟠 | audiencia.json | `modalidade` sem opção **Híbrida** (regra workspace) |
| 🟠 | parcela vs pagamento | Status **Recebida** vs **Recebido** — vocabulário inconsistente |
| 🟠 | test_scheduler.py:87–92 | Teste `test_notificar_audiencias_amanha_nao_dispara` sempre passa (`pass`) |
| 🟡 | servico_link.js:12 | Referência `cliente_name` inexistente em servico.json (branch morta) |
| 🟡 | documentos.py | `gerar_documento` sem check Template Documento; só usado em testes |
| 🟡 | tasks.py:312 | `verificar_status_servicos` arquiva sem notificar usuário |
| 🟡 | parcela_de_honorarios.py:16 | String corrompida encoding (`nĂŁo`) em mensagem throw |

### 13.2 Inconsistências de Dados

| Sev | Item |
|-----|------|
| 🟡 | Registro de Atos / Acordo: `title_field=servico` (Link ID, não título legível) |
| 🟡 | Acordo child table fieldname `table_ztjx` (não descritivo) |
| 🟡 | Comarca field `city` vs convenção `cidade` |
| 🟡 | Fase/Vara/Tribunal/Comarca: fieldnames inglês (`phase_name`, `vara_name`) vs labels PT |
| 🟡 | Pagamento/Tarefa/Comunicacao/Cliente: `autoname` sem `naming_rule` no JSON |
| 🟡 | Registro de Atos JSON: duplicate `idx` 17–18 |
| 🟢 | Tribunal jurisdiction inclui **Eleitoral** (extra vs .cursorrules) |

### 13.3 Violações de Padrão Frappe v16

| Sev | Arquivo:Linha | Problema |
|-----|---------------|----------|
| 🟠 | documentos.py:515,554 | `frappe.db.commit()` em whitelisted handler |
| 🟠 | painel_api.py:935,954 | `frappe.db.commit()` em API |
| 🟠 | financeiro.py (múltiplas) | commit em sync hooks/API |
| 🟠 | tasks.py:33,48,81,126,315 | commit em schedulers |
| 🟠 | registro_de_horas.py:34,53 | commit após timer save |
| 🟡 | documentos.get_placeholders_* | whitelist sem checagem permissão |
| 🟡 | servico.get_link_title | override global sem check |
| 🟡 | despesa.gerar_proxima_despesa | insert ignore_permissions sem role check |
| 🟡 | registro_de_horas timer | save ignore_permissions |
| 🟡 | calendar_sync.py:62,65 | Event insert/save ignore_permissions |
| 🟡 | comunicacao.py:36 | Tarefa insert ignore_permissions |

### 13.4 Code Smells e Débito Técnico

| Sev | Arquivo | Problema |
|-----|---------|----------|
| 🟡 | painel_api.py | `LIMITS` dict L28–34 nunca usado (dead code) |
| 🟡 | financeiro.py:386–410 | `_exibir_resultado_bulk_delete` nunca chamada |
| 🟡 | tasks.py:195–205 | `_parcela_recipients` nunca chamada |
| 🟡 | documentos.py | `get_placeholders_disponiveis`, `gerar_documento` dead em produção |
| 🟡 | setup/translations.py:44–45 | `except Exception: pass` silencioso |
| 🟡 | painel_api.py:894 | `except Exception:` em `_vara_label` |
| 🟡 | Funções >50 linhas | get_painel_data, _build_context, sincronizar_pagamento_atos, notificar_prazos_diario |
| 🟡 | Pagamento | double on_update handler (tasks + financeiro) — redundante |
| 🟢 | README.md:35 | Contagem testes 149 vs 167 real |

### 13.5 Segurança

| Sev | Arquivo | Problema |
|-----|---------|----------|
| 🟠 | documentos.get_placeholders_referencia | Exposto sem auth check (dados estrutura, baixo risco) |
| 🟡 | SQL painel_api | Parametrizado ✅ — sem injection detectada |
| 🟡 | ignore_permissions | Usado em sync/calendar/timer — justificável mas amplo |
| 🟢 | XSS | Text Editor fields padrão Frappe; painel renderiza escaped |

### 13.6 Performance

| Sev | Arquivo:Linha | Problema |
|-----|---------------|----------|
| 🟠 | notificacoes.py:12–25 | get_all prazos sem limit_page_length |
| 🟠 | painel_api.py:628–636,662–670,743–770 | N+1 get_value em loops |
| 🟠 | documentos.py:589–596 | get_all por kit (N+1) |
| 🟠 | tasks.py:273–293 | verificar_status_servicos N+1 db.count |
| 🟡 | get_painel_data | Múltiplas queries agregadas — aceitável para dashboard |

### 13.7 Integridade Hooks ↔ Código

**Resultado:** 22/22 referências em hooks.py resolvem ✅ (verificação import paths).

**Divergência documentação:** `.cursorrules` cita `notificacoes.verificar_prazos` / `verificar_parcelas_vencidas` em notificacoes.py — implementação real em `tasks.py` + `notificar_prazos_diario`.

### 13.8 Integridade Sidebar ↔ DocTypes

| Check | Resultado |
|-------|-----------|
| 26 sidebar links | 26/26 targets existem ✅ |
| DocTypes standalone fora sidebar | 0 (child tables omitidas by design ✅) |
| Workspace content shortcuts | 2 órfãos: Faturas, Cadastro de documentos 🟡 |
| Workspace links vs sidebar | 5 itens sidebar ausentes no workspace links 🟡 |

### 13.9 Resumo da Auditoria

| Severidade | Contagem | Exemplos |
|------------|----------|----------|
| 🔴 Crítico | 0 | — |
| 🟠 Alto | 12 | commits em API/scheduler; N+1 notificacoes; whitelist sem perm; cobranca_id Data |
| 🟡 Médio | 28 | dead code; title_field Link; naming_rule gaps; test stub; hex colors painel |
| 🟢 Baixo | 8 | idx duplicado; README desatualizado; Eleitoral extra; encoding string |

---

## 14. RECOMENDAÇÕES

### Quick wins (< 30min cada)

1. Corrigir `test_notificar_audiencias_amanha_nao_dispara` — adicionar `assert_not_called` filtrado.
2. Atualizar README contagem testes 149 → 167.
3. Remover dead code: `LIMITS`, `_exibir_resultado_bulk_delete`, `_parcela_recipients`.
4. Substituir hex colors em `painel.js:2750–2753` por CSS vars Frappe.
5. Remover referência `cliente_name` em `servico_link.js:12`.
6. Corrigir encoding `parcela_de_honorarios.py:16`.
7. Renomear/corrigir shortcuts órfãos no workspace content (Faturas → Pagamentos).

### Médio prazo (1–4h cada)

1. Adicionar `naming_rule` ausente nos DocTypes com autoname.
2. Migrar `cobranca_id` Ato Advocaticio para Link→Pagamento.
3. Adicionar Híbrida em Audiencia.modalidade.
4. Padronizar status Recebido/Recebida entre Pagamento e Parcela.
5. Adicionar permission checks em placeholders API e gerar_proxima_despesa.
6. Reduzir `frappe.db.commit()` desnecessários (confiar auto-commit Frappe).
7. Otimizar N+1 em painel_api e get_kits_disponiveis.
8. Testes CRUD: Comarca, Vara, Tribunal, Fase, Config Escritório, Kit Documentos.
9. Testes reports: inadimplencia, fluxo_de_caixa, honorarios_por_cliente, carteira_ativa.
10. Sincronizar workspace links com sidebar (Comunicacao, Horas, Custas, Despesas).

### Refatoração estrutural (1+ dia)

1. Quebrar `painel_api.py` (~900+ linhas) em módulos por domínio (KPIs, financeiro, timeline).
2. Unificar pipeline Pagamento on_update (tasks + financeiro) em handler único.
3. Renomear `table_ztjx` → `parcelas` via Property Setter + migração dados.
4. Alinhar fieldnames auxiliares para inglês consistente (city→cidade ou documentar exceção).
5. Implementar Notification nativa para parcelas (regra .cursorrules) além de enqueue manual.
6. Substituir `notificar_prazos_diario` email HTML inline por Notification DocType configurável.

---

*Gerado em 2026-05-31. Para regenerar: re-executar inventário `find` + leitura integral dos fontes.*
