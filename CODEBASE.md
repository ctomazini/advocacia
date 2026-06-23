# CODEBASE — App Advocacia (Frappe v16)

> Gerado em **2026-06-23** — inventário pós-v1.1.0 (UX final + hub pills + Office Settings CPF/RG). Branch **`ux/step-09-final-polish`**.

> **HEAD:** `f92a013` — feat(office-settings): lawyer CPF/RG + placeholders

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | advocacia |
| Versão | 1.1.0 (`pyproject.toml`, `advocacia.__version__`) |
| Framework | Frappe v16.19.0 |
| Licença | MIT |
| Branch | main |
| Remote | git@github.com:ctomazini/advocacia.git |
| Site dev | advocacia.local (porta 8000) |
| Linhas Python | ~15669 |
| Linhas JavaScript | ~279836 |
| Métodos de teste | 291 |
| DocTypes | 24 (todos `custom: 0`) |
| Script Reports | 6 |

**Propósito:** LegalTech BR — clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas, registro de horas, painel, documentos `.docx`.

**Deps:** `docxtpl>=0.18.0`; jquery.inputmask (Frappe).

### 1.1 Entregas recentes (jun/2026)

| Área | Mudança |
| --- | --- |
| **v1.1.0** | UX Etapas 07–09; hub pills; download docx; Office Settings CPF/RG advogada |
| **v1.0.0** | 24 DocTypes renomeados PT→EN; tabs no painel; tag `v1.0.0` |
| **Office Settings** | Logo, dados bancários, `default_notify_days`; seed idempotente |
| **Documentos** | Referência completa de placeholders; logo inline docx; botão no Legal Case |
| **IA** | `agent_api.py` (4 endpoints read-only) + `test_agent_api.py` |
| **Form layout** | Column Breaks em 10 DocTypes satélites + 3 auxiliares (exc. Legal Case hub) |
| **Relatórios P1** | `boot.py`, `reports.css`, `reports_common.js`, print formats Report (9) |
| **Sidebar** | Labels PT sincronizados com workspace e traduções |
| **Legal Payment** | Fix coluna Origem na list view |

**Commits recentes:**
```text
cc3a398 docs: sync codebase, audits and README for P1 reports and P2 painel
f2a8b1f docs(painel): sync audit_dashboard with modular P2 structure
dda3bea refactor(painel): extract main.js orchestrator and remove dead audiencias module
b275497 test(reports): add boot_session and print format tests
5091743 feat(reports): integrate report helpers in Script Report JS files
28bb4f6 feat(reports): add print format templates for Script Reports
20e4d96 feat(reports): add global report CSS and JS helpers
c18402d feat(reports): add boot_session for office branding in prints
4ef63ef refactor(painel): P0 layout with stacked finance zone
d27c9f7 test(Hub): add case_hub tests
07c17a9 feat(Hub): register case_hub.js and case_hub.css in app includes
a759a78 feat(Hub): restructure Legal Case with 6 tabs and 12 HTML panels
```

## 2. Árvore de Arquivos (anotada)

```text
advocacia/
├── CODEBASE.md, README.md, pyproject.toml
└── advocacia/
    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/
    ├── fixtures/, workspace_sidebar/advocacia.json
    ├── public/js/ (masks, list_nav, reports_common, painel/* page-scoped, …)
    ├── public/css/ (list_filters, case_hub, reports)
    ├── boot.py, print_formats/reports/
    └── advocacia/
        ├── validators.py, titulos.py, agent_api.py, painel_api.py (facade)
        ├── painel/ (__init__, _helpers, kpis, financeiro, prazos, timeline, agenda, atencao, saude, operational)
        ├── documentos.py, financeiro.py, tasks.py, notificacoes.py, calendar_sync.py
        ├── setup/ (install, sidebar, workspace, reports, translations, seed_demo)
        ├── tests/ (33 arquivos), doctype/ (24), page/painel/, report/ (6), workspace/
```

## 3. Mapa de DocTypes (24)

Colunas: `fieldname` | label | fieldtype | options | reqd | unique. Section/Column/Tab breaks omitidos.

#### Standalone / transacionais

### Case Communication

**Meta:** autoname=`format:COM-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case |  |  |
| client | Client | Link | Client | ✓ |  |
| communication_date | Data | Datetime |  | ✓ |  |
| type | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtua... | ✓ |  |
| subject | Assunto | Data |  | ✓ |  |
| summary | Resumo | Text Editor |  |  |  |
| next_steps | Próximos Passos | Small Text |  |  |  |
| generate_task | Gerar Legal Task | Check |  |  |  |
| legal_task | Legal Task Gerada | Link | Legal Task |  |  |
| title | Título | Data |  |  |  |

### Client

**Meta:** autoname=`format:CLI-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`client_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| person_type | Tipo de Pessoa | Select | Pessoa Física Pessoa Jurídica | ✓ |  |
| client_name | Nome / Razão Social | Data |  | ✓ |  |
| trade_name | Nome Fantasia | Data |  |  |  |
| cpf | CPF | Data |  |  | ✓ |
| rg | RG | Data |  |  |  |
| cnpj | CNPJ | Data |  |  | ✓ |
| nationality | Nacionalidade | Data |  |  |  |
| marital_status | Estado Civil | Select |  Solteiro(a) Casado(a) Divorciado(a) Viúvo(a) União Estável |  |  |
| occupation | Profissão | Data |  |  |  |
| representative | Representante Legal | Data |  |  |  |
| representative_cpf | CPF do Representante | Data |  |  |  |
| representative_role | Cargo | Data |  |  |  |
| representative_nationality | Nacionalidade do Representante | Data |  |  |  |
| contacts | Contatos | Table | Client Contact |  |  |
| addresses | Endereços | Table | Client Address |  |  |
| remarks | Observações | Text Editor |  |  |  |

### Court Cost

**Meta:** autoname=`format:CUST-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| type | Tipo | Select | Taxa Judicial Perícia Certidão Deslocamento Cópia/Impress... | ✓ |  |
| description | Descrição | Data |  | ✓ |  |
| status | Status | Select | Pendente Pago Repassado Cancelado |  |  |
| amount | Valor | Currency |  | ✓ |  |
| payment_date | Data de Legal Payment | Date |  |  |  |
| bill_to_client | Repassar ao Client | Check |  |  |  |
| transfer_date | Data de Repasse | Date |  |  |  |
| payment_method | Forma de Legal Payment | Select | PIX TED Boleto Dinheiro Cartão |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Deadline

**Meta:** autoname=`format:PRAZO-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| due_date | Data do Prazo | Date |  | ✓ |  |
| status | Status | Select | Pendente Concluído Vencido |  |  |
| description | Descrição | Small Text |  | ✓ |  |
| priority | Prioridade | Select | Alta Média Baixa |  |  |
| responsible | Responsável | Link | User |  |  |
| notification_days | Notificar com antecedência (dias) | Int |  |  |  |
| remarks | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Document Kit

**Meta:** autoname=`field:title` · naming_rule=`By fieldname` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  | ✓ | ✓ |
| description | Descrição | Small Text |  |  |  |
| enabled | Habilitado | Check |  |  |  |
| templates | Templates | Table | Document Kit Item | ✓ |  |

### Document Template

**Meta:** autoname=`field:title` · naming_rule=`By fieldname` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Titulo | Data |  | ✓ | ✓ |
| document_type | Tipo de Documento | Select | Contrato Declaracao Recibo Carta Ficha de Atendimento Outro | ✓ |  |
| description | Descricao | Small Text |  |  |  |
| enabled | Habilitado | Check |  |  |  |
| template_file | Arquivo Template (.docx) | Attach |  | ✓ |  |
| show_placeholders | Ver Placeholders Disponíveis | Button |  |  |  |

### Fee Agreement

**Meta:** autoname=`format:ACOR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| fee_mode | Modo | Select | Honorários Diretos Acordo com Divisão | ✓ |  |
| status | Status | Select | Vigente Encerrado Cancelado Quitado |  |  |
| total_agreement_value | Valor Total do Acordo | Currency |  |  |  |
| lawyer_percentage | Percentual Advogada (%) | Percent |  |  |  |
| fixed_fee_amount | Valor Fixo de Honorários | Currency |  |  |  |
| lawyer_amount | Valor Advogada | Currency |  |  |  |
| billing_type | Tipo de cobrança | Select | Valor fixo Percentual do acordo Percentual da causa Misto | ✓ |  |
| client_percentage | Percentual Client | Percent |  |  |  |
| client_amount | Valor Client | Currency |  |  |  |
| calculation_type | Tipo de cálculo | Select | Percentual Valor fixo |  |  |
| contingency_fee_pct | Percentual Sucumbência (%) | Percent |  |  |  |
| contingency_fee_amount | Honorários de Sucumbência | Currency |  |  |  |
| contingency_fee_status | Status da Sucumbência | Select | A definir Deferida Indeferida Paga |  |  |
| installment_count | Número de Parcelas | Int |  |  |  |
| first_installment_date | Data Primeira Parcela | Date |  |  |  |
| installment_amount | Valor da Parcela | Currency |  |  |  |
| generate_installments | Gerar Parcelas | Button |  |  |  |
| fee_installments |  | Table | Fee Installment |  |  |
| lawyer_total | Total Advogada | Currency |  |  |  |
| client_total | Total Client | Currency |  |  |  |
| remarks | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Hearing

**Meta:** autoname=`format:AUD-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| hearing_datetime | Data e Hora | Datetime |  | ✓ |  |
| status | Status | Select | Agendada Realizada Adiada Cancelada |  |  |
| type | Tipo | Select | Conciliação Instrução Julgamento Una | ✓ |  |
| modality | Modalidade | Select | Presencial Virtual Híbrida |  |  |
| link_virtual | Link da Audiência Virtual | Data | URL |  |  |
| court_branch | Court Branch | Link | Court Branch |  |  |
| outcome | Resultado | Select |  Realizada Adiada Acordo Sem acordo |  |  |
| remarks | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Legal Case

**Meta:** autoname=`format:SERV-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| hub_summary_bar | Resumo do Serviço | HTML |  |  |  |
| client | Client | Link | Client | ✓ |  |
| type | Tipo | Select | Processo Judicial Consultoria Contrato Diligência Adminis... | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Em andamento Encerrado Suspenso Arquivado |  |  |
| case_phase | Case Phase | Link | Case Phase |  |  |
| opening_date | Data de Abertura | Date |  |  |  |
| case_number | Número do Processo | Data |  |  |  |
| legacy_numbering | Numeração legada (pré-CNJ) | Check |  |  |  |
| area | Área | Select |  Família Trabalhista Cível Criminal Previdenciário Admini... |  |  |
| court_branch_link | Court Branch | Link | Court Branch |  |  |
| court | Court | Link | Court |  |  |
| jurisdiction | Jurisdiction | Link | Jurisdiction |  |  |
| opposing_party | Parte Contrária | Data |  |  |  |
| case_value | Valor da Causa | Currency |  |  |  |
| remarks | Observações | Text Editor |  |  |  |
| phases_panel | Fase Processual | HTML |  |  |  |
| hearings_panel | Audiências | HTML |  |  |  |
| financial_summary_panel | Resumo Financeiro | HTML |  |  |  |
| installments_panel | Parcelas | HTML |  |  |  |
| payments_panel | Pagamentos | HTML |  |  |  |
| court_costs_panel | Custas Processuais | HTML |  |  |  |
| deadlines_panel | Prazos | HTML |  |  |  |
| tasks_panel | Tarefas | HTML |  |  |  |
| communications_panel | Comunicações | HTML |  |  |  |
| service_records_panel | Registro de Atos | HTML |  |  |  |
| time_entries_panel | Registro de Horas | HTML |  |  |  |
| document_kits_panel | Kits de Documentos | HTML |  |  |  |

### Legal Payment

**Meta:** autoname=`format:PAG-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| origin_type | Origem | Select | Honorários (Parcela) Atos Advocatícios |  |  |
| fee_agreement | Acordo | Link | Fee Agreement |  |  |
| service_record | Service Record | Link | Service Record |  |  |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client | ✓ |  |
| installment_number | Nº Parcela | Int |  |  |  |
| description | Descrição | Small Text |  |  |  |
| installment_origin_id | ID Origem | Data |  |  | ✓ |
| synced_at | Sincronizado em | Datetime |  |  |  |
| manual_override | Edição manual (não sincronizar) | Check |  |  |  |
| amount | Valor | Currency |  | ✓ |  |
| received_amount | Valor Recebido | Currency |  |  |  |
| due_date | Vencimento | Date |  | ✓ |  |
| received_date | Data de Recebimento | Date |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Cancelado Renegociado Repassado | ✓ |  |
| remarks | Observações | Small Text |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| title | Título | Data |  |  |  |

### Legal Task

**Meta:** autoname=`format:TAR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case |  |  |
| client | Client | Link | Client |  |  |
| subject | Descrição da Legal Task | Data |  | ✓ |  |
| status | Status | Select | Pendente Em Andamento Concluída Cancelada |  |  |
| priority | Prioridade | Select | Normal Alta Urgente |  |  |
| due_date | Data Limite | Date |  |  |  |
| description | Descrição | Text Editor |  |  |  |
| responsible | Responsável | Link | User |  |  |
| completion_date | Data de Conclusão | Date |  |  |  |
| title | Título | Data |  |  |  |

### Office Expense

**Meta:** autoname=`format:DESP-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| description | Descrição | Data |  | ✓ |  |
| category | Categoria | Select | Aluguel Energia Água Internet Telefone Software/Assinatur... | ✓ |  |
| amount | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Pago Atrasado Cancelado |  |  |
| due_date | Data de Vencimento | Date |  |  |  |
| payment_date | Data de Legal Payment | Date |  |  |  |
| payment_method | Forma de Legal Payment | Select | PIX TED Boleto Dinheiro Cartão Débito Automático |  |  |
| is_recurring | Despesa Recorrente | Check |  |  |  |
| frequency | Frequência | Select | Mensal Bimestral Trimestral Semestral Anual |  |  |
| next_due_date | Próximo Vencimento | Date |  |  |  |
| receipt | Comprovante | Attach |  |  |  |
| remarks | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Service Record

**Meta:** autoname=`format:ATOS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| status | Status | Select | Em aberto Parcialmente cobrado Cobrado |  |  |
| opening_date | Data de Abertura | Date |  |  |  |
| acts |  | Table | Legal Act Item |  |  |
| pending_total | Total Pendente | Currency |  |  |  |
| billed_total | Total Cobrado | Currency |  |  |  |
| grand_total | Total Geral | Currency |  |  |  |
| billing_due_date | Vencimento da Cobrança | Date |  |  |  |
| last_payment | Último Legal Payment | Link | Legal Payment |  |  |
| generate_billing | Sincronizar Cobrança | Button |  |  |  |
| remarks | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Time Entry

**Meta:** autoname=`format:HRS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| entry_date | Data | Date |  | ✓ |  |
| responsible | Responsável | Link | User |  |  |
| start_time | Hora Início | Time |  |  |  |
| end_time | Hora Fim | Time |  |  |  |
| duration_minutes | Duração (min) | Int |  |  |  |
| duration_hours | Duração (horas) | Float |  |  |  |
| activity | Atividade | Data |  | ✓ |  |
| category | Categoria | Select | Estudo/Pesquisa Redação Audiência Reunião Deslocamento At... |  |  |
| billable | Cobrável | Check |  |  |  |
| description | Detalhes | Small Text |  |  |  |
| timer_display | Tempo Decorrido | HTML |  |  |  |
| timer_start | Início do Timer | Datetime |  |  |  |
| timer_active | Timer Ativo | Check |  |  |  |
| title | Título | Data |  |  |  |

#### Auxiliares (cadastro rígido)

### Case Phase

**Meta:** autoname=`field:case_phase_name` · naming_rule=`By fieldname` · title_field=`case_phase_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| case_phase_name | Nome da Fase | Data |  | ✓ | ✓ |
| sort_order | Ordem | Int |  |  |  |

### Court

**Meta:** autoname=`field:court_name` · naming_rule=`By fieldname` · title_field=`court_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| court_name | Nome do Court | Data |  | ✓ | ✓ |
| abbreviation | Sigla | Data |  | ✓ | ✓ |
| jurisdiction | Esfera | Select | Estadual Federal Trabalho Superior Militar Eleitoral | ✓ |  |

### Court Branch

**Meta:** autoname=`field:court_branch_name` · naming_rule=`By fieldname` · title_field=`court_branch_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| court_branch_name | Nome da Court Branch | Data |  | ✓ | ✓ |
| jurisdiction | Jurisdiction | Link | Jurisdiction | ✓ |  |
| court_type | Tipo | Select | Cível Criminal Família Trabalho Federal Juizado Especial ... |  |  |

### Jurisdiction

**Meta:** autoname=`field:jurisdiction_name` · naming_rule=`By fieldname` · title_field=`jurisdiction_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| jurisdiction_name | Nome da Jurisdiction | Data |  | ✓ | ✓ |
| uf | UF | Select | AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ ... | ✓ |  |
| city | Cidade | Data |  |  |  |

#### Child tables

### Client Address

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| type | Tipo | Select | Residencial Comercial Correspondência Outro |  |  |
| cep | CEP | Data |  |  |  |
| street | Logradouro | Data |  | ✓ |  |
| number | Número | Data |  |  |  |
| complement | Complemento | Data |  |  |  |
| neighborhood | Bairro | Data |  |  |  |
| city | Cidade | Data |  |  |  |
| state | Estado | Select |  AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ... |  |  |
| is_primary | Endereço Principal | Check |  |  |  |

### Client Contact

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| contact_name | Nome | Data |  | ✓ |  |
| type | Tipo | Select | Principal Conjuge Responsável Outro |  |  |
| phone | Telefone | Data |  |  |  |
| mobile | Celular | Data |  |  |  |
| email | E-mail | Data | Email |  |  |
| remarks | Observação | Small Text |  |  |  |

### Document Kit Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| template | Template | Link | Document Template | ✓ |  |
| display_order | Ordem | Int |  |  |  |

### Fee Installment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| due_date | Vencimento | Date |  | ✓ |  |
| total_amount | Valor Total | Currency |  |  |  |
| lawyer_amount | Valor Advogada | Currency |  |  |  |
| contingency_amount | Valor Sucumbência | Currency |  |  |  |
| client_amount | Valor Client | Currency |  |  |  |
| description | Descrição | Small Text |  |  |  |
| installment_origin_id | ID de Origem | Data |  |  |  |
| payment | Legal Payment | Link | Legal Payment |  |  |
| status | Status | Select | Pendente Vencido Recebido Repassado Cancelado |  |  |
| received_date | Data de Recebimento | Date |  |  |  |
| transfer_date | Data de Repasse ao Client | Date |  |  |  |
| payment_method | Forma de Recebimento | Select |  PIX TED Dinheiro Cartão Boleto |  |  |
| remarks | Observação | Small Text |  |  |  |

### Legal Act Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| act_date | Data | Date |  | ✓ |  |
| type | Tipo | Select | Inicial Audiência Defesa Diligência Consulta Contrato Adm... | ✓ |  |
| description | Descrição | Small Text |  |  |  |
| amount | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Cobrado |  |  |
| payment | Legal Payment | Link | Legal Payment |  |  |

#### Single

### Office Settings

**Meta:** autoname=`Office Settings` · naming_rule=`Expression` · title_field=`` · istable=0 · issingle=1

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| company_name | Razão Social | Data |  | ✓ |  |
| cnpj | CNPJ | Data |  |  |  |
| sia_registration | Registro SIA | Data |  |  |  |
| office_logo | Logo do Escritório | Attach Image |  |  |  |
| lawyer_name | Advogada(o) Principal | Data |  | ✓ |  |
| lawyer_cpf | CPF da Advogada(o) | Data |  |  |  |
| lawyer_rg | RG da Advogada(o) | Data |  |  |  |
| oab | OAB | Data |  | ✓ |  |
| default_notify_days | Dias padrão de antecedência (prazos) | Int |  |  |  |
| address | Endereço Completo | Small Text |  | ✓ |  |
| bank_name | Banco | Data |  |  |  |
| bank_agency | Agência | Data |  |  |  |
| bank_account | Conta | Data |  |  |  |
| bank_pix | Chave PIX | Data |  |  |  |

### Grafo de links (resumo)

`Client` ← Legal Case, Legal Payment, Acordo, … · `Jurisdiction` ← Court Branch, Legal Case · `Legal Case` hub → Prazos, Hearing, Atos, Horas, Custas · `Acordo` → `Fee Installment` → Legal Payment · `Service Record` → `Legal Act Item` (`cobranca_id` Link Legal Payment) · Auxiliares: Jurisdiction, Court Branch, Court, Case Phase.

## 4. hooks.py

### fixtures
Workspace Advocacia; Notifications prazo/audiência; Custom Field Event `custom_source%`.

### boot_session
- `advocacia.boot.boot_session` → `frappe.boot.adv_office` (Office Settings para prints)

### app_include_css
- `/assets/advocacia/css/list_filters.css`
- `/assets/advocacia/css/case_hub.css`
- `/assets/advocacia/css/reports.css`

### app_include_js
- `/assets/advocacia/js/masks.js`
- `/assets/advocacia/js/documentos_placeholders.js`
- `/assets/advocacia/js/list_nav.js`
- `/assets/advocacia/js/list_filters.js`
- `/assets/advocacia/js/cliente_from_servico.js`
- `/assets/advocacia/js/timer_global.js`
- `/assets/advocacia/js/case_hub.js`
- `/assets/advocacia/js/reports_common.js`

**Painel (page-scoped):** `page/painel/painel.js` → `frappe.require(PAINEL_ASSETS)` — 14 módulos em `public/js/painel/` (utils, hero, kpis, saude, atencao, agenda, timeline, financeiro, operational, refresh, sections, handlers, main, index).

**Removidos:** `navegacao.js`, widget painel global, `servico_link.js`, `audiencias.js` (morto).

### doc_events

| DocType | Evento | Handler |
| --- | --- | --- |
| Fee Agreement | on_update | financeiro.sincronizar_pagamentos_hook |
| Fee Installment | on_update | tasks.on_parcela_update |
| Legal Payment | on_update | financeiro.processar_pagamento_on_update |
| Legal Payment | on_trash | financeiro.on_pagamento_trash |
| Hearing | after_insert / on_update | calendar_sync.sync_audiencia_to_event |
| Deadline | after_insert / on_update | calendar_sync.sync_prazo_to_event |

### scheduler_events
- **daily:** verificar_parcelas_vencidas, verificar_despesas_vencidas, notificar_parcelas_vencidas, notificar_audiencias_hoje, notificar_prazos_diario
- **weekly:** verificar_status_servicos

### after_migrate
reinstalar_istable → after_install → event fields → translations → sidebar → reports → workspace

## 5. API whitelisted

| Função | Módulo | Permissão | Chamador |
| --- | --- | --- | --- |
| get_painel_data | painel_api → painel.get | Legal Case read | painel.js xcall |
| marcar_parcela_recebida | painel_api → painel.financeiro | Legal Payment write | painel.js |
| legal_case_query | legal_case | query | Link Legal Case |
| gerar_documento_servico / em_lote | documentos | Legal Case read/write | servico.js |
| get_kits_disponiveis | documentos | read | servico.js |
| get_placeholders_referencia | documentos | Template read | document_template.js |
| get_active_cases / get_case_summary | agent_api | Legal Case read | MCP / agente IA |
| get_court_costs_by_type | agent_api | Manager + Court Cost read | MCP / agente IA |
| get_financial_overview | agent_api | Manager + Legal Payment read | MCP / agente IA |
| registrar_recebimento/repasse | parcela | write | form |
| concluir | legal_task | write | tarefa.js |
| timer APIs | registro_de_horas | write | timer_global.js |
| get_events | audiencia/prazos | calendar read | *_calendar.js |
| gerar_proxima_despesa | despesa | create | form |
| financeiro sync | financeiro | has_permission | hooks |

**xcall:** `advocacia.advocacia.painel_api.get_painel_data` (facade — não alterar no JS).

## 6. Schedulers

Ver §4 (`tasks.py`, `notificacoes.py`). Sem `commit()` em request/scheduler.

## 7. Client JS

- Globais: máscaras, list_nav, list_filters, reports_common, case_hub, timer.
- **Painel modular** (~2.490 linhas JS + 2.130 CSS): orquestrador `main.js` (`load`/`render`); `index.js` bootstrap; CSS vars para charts; carregado só na Page `painel`.
- Calendários: `hearing_calendar.js`, `deadline_calendar.js`.

## 8. Setup / migrations

Idempotente; `commit()` só em setup/patches/seed (`seed_demo.py` = dev only).

## 9. Reports (6)

- carteira_ativa
- fluxo_de_caixa
- honorarios_por_cliente
- inadimplencia
- horas_por_servico
- produtividade

Status Legal Payment: Pendente, Vencido, Recebido, Cancelado, Renegociado, Repassado.

## 10. Fixtures / Workspace / Sidebar

- 26 links sidebar ↔ workspace.
- Seções com `collapsible: 1` (Frappe v16).

## 11. Testes

- **291** métodos em **45** arquivos.
- `bench --site advocacia.local run-tests --app advocacia`
- Última run (site dev): **291** testes, **OK** (jun/2026).

## 12. Integrações

- calendar_sync → Event; documentos → docxtpl; Office Settings (logo, banco, prazos); `agent_api.py` para agentes IA.

## 13. Backlog consciente

1. Chart.js → frappe.ui.Chart
2. Fieldnames EN auxiliares residuais (`city`, `phase_name`)
3. Migrar sql → qb no painel
4. OpenAPI / tools MCP espelhando `agent_api.py`

## 14. Re-audit e prontidão para produção

### 14.1 Checklist (13 categorias)

| # | Categoria | Status | Notas |
| --- | --- | --- | --- |
| 1 | Naming / autoname | ✅ | {YYYY} + Expression nos transacionais |
| 2 | Link vs Data | ✅ | Auxiliares + pagamento em atos (fieldname cobranca_id) |
| 3 | Validators | ✅ | validators.py + controllers |
| 4 | db.commit | ✅ | Só setup/patches/seed/backfill |
| 5 | ignore_permissions | ⚠️ | comunicacao, calendar_sync; seed_demo dev |
| 6 | Whitelisted | ✅ | permission checks nos endpoints críticos |
| 7 | N+1 / limits | ✅ | painel refatorado |
| 8 | Dead code | ✅ | P0–P4b limpeza |
| 9 | JS = UX | ✅ | Negócio em Python |
| 10 | Hooks | ✅ | Legal Payment handler único; schedulers |
| 11 | Workspace/sidebar | ✅ | collapsible fix |
| 12 | Testes | ✅ | 291/291 OK |
| 13 | Reinstall limpo | ⏳ | Obrigatório pré go-live |

### 14.2 Ajustes de teste (2026-06-02)

- `test_titulos`: expectativa `{ID} — {descritor}` quando o usuário define título manual.
- `test_criar_pj_valido`: CNPJ único via `_gerar_cnpj_valido()`.
- `test_sem_prazos_urgentes_nao_envia`: mock de `get_all` isolado de dados demo.

### 14.3 Veredito

| Critério | OK? |
| --- | --- |
| Código Git (custom:0) | ✅ |
| Blocos auditoria 1–4 | ✅ |
| UX jun/2026 | ✅ (smoke manual) |
| Suite 291/291 verde | ✅ |
| install-app site limpo | ⏳ recomendado pré go-live |

**Conclusão:** código e testes **prontos para produção**; validar reinstall limpo e smoke manual do painel/sidebar antes do go-live.

---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
