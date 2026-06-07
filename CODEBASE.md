# CODEBASE — App Advocacia (Frappe v16)

> Gerado em **2026-06-07** — re-audit pós-UX (títulos, list views, sidebar, painel). Branch **`frappe-v16`**. Frappe puro, **sem ERPNext**.

> **HEAD:** `02a393d 2026-06-07 17:22:44 +0000 refactor!: rename 24 DocTypes PT→EN and release v1.0.0`

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | advocacia |
| Versão | 1.0.0 (`pyproject.toml`) |
| Framework | Frappe v16.19.0 |
| Licença | MIT |
| Branch | frappe-v16 |
| Remote | git@github.com:ctomazini/advocacia.git |
| Site dev | advocacia.local (porta 8000) |
| Linhas Python | ~13167 |
| Linhas JavaScript | ~5669 |
| Métodos de teste | 245 |
| DocTypes | 24 (todos `custom: 0`) |
| Script Reports | 6 |

**Propósito:** LegalTech BR — clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas, registro de horas, painel, documentos `.docx`.

**Deps:** `docxtpl>=0.18.0`; jquery.inputmask (Frappe).

### 1.1 Entregas recentes (jun/2026)

| Área | Mudança |
| --- | --- |
| **v1.0.0** | 24 DocTypes renomeados PT→EN; tabs no painel; tag `v1.0.0` |
| **Office Settings** | Logo, dados bancários, `default_notify_days`; seed idempotente |
| **Documentos** | Referência completa de placeholders; logo inline docx; botão no Legal Case |
| **IA** | `agent_api.py` (4 endpoints read-only) + `test_agent_api.py` |
| **Painel** | Chaves EN backend/frontend; handlers KPI; soft refresh |
| **Relatórios** | 6 reports com KPIs, gráficos e linha Total padronizados |
| **Sidebar** | Labels PT sincronizados com workspace e traduções |
| **Legal Payment** | Fix coluna Origem na list view |

**Commits recentes:**
```text
02a393d refactor!: rename 24 DocTypes PT→EN and release v1.0.0
083b027 docs: move audit-deploy-ready.md into advocacia/docs index folder
b83371e chore: bump version to 0.7.1 and add deploy-ready audit report
114c3e7 style: convert spaces to tabs in Python files for consistency
0c5740d fix: add explicit limit_page_length to scheduler and documentos queries
6c09732 fix: remove resync commit=True and harden gerar_pagamento_atos whitelist
1aa3f8a fix: reorder duplicate idx in Acordo, Audiencia and Controle de Prazos
a149418 fix: add explicit naming_rule to auxiliary DocTypes and Configuracao Single
0608589 fix: replace deprecated cur_frm in list_nav.js with Frappe v16 API
5444bb0 chore: add advocacia-predeploy cursor rule for v0.7.1 fixes
28467df docs: organize documentation for filters, connections and E2E
cf33fc5 test: add Playwright E2E script for Advocacia UI flow
```

## 2. Árvore de Arquivos (anotada)

```text
advocacia/
├── CODEBASE.md, README.md, pyproject.toml
└── advocacia/
    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/
    ├── fixtures/, workspace_sidebar/advocacia.json
    ├── public/js/ (masks, documentos_placeholders, painel/*, list_nav, …)
    └── advocacia/
        ├── validators.py, titulos.py, agent_api.py, painel_api.py (facade)
        ├── painel/ (kpis, financeiro, prazos, timeline, _helpers)
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
| data | Data | Datetime |  | ✓ |  |
| tipo | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtua... | ✓ |  |
| assunto | Assunto | Data |  | ✓ |  |
| resumo | Resumo | Text Editor |  |  |  |
| proximos_passos | Próximos Passos | Small Text |  |  |  |
| gerar_tarefa | Gerar Legal Task | Check |  |  |  |
| legal_task | Legal Task Gerada | Link | Legal Task |  |  |
| title | Título | Data |  |  |  |

### Client

**Meta:** autoname=`format:CLI-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`nome` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tipo_pessoa | Tipo de Pessoa | Select | Pessoa Física Pessoa Jurídica | ✓ |  |
| nome | Nome / Razão Social | Data |  | ✓ |  |
| nome_fantasia | Nome Fantasia | Data |  |  |  |
| cpf | CPF | Data |  |  | ✓ |
| rg | RG | Data |  |  |  |
| cnpj | CNPJ | Data |  |  | ✓ |
| nacionalidade | Nacionalidade | Data |  |  |  |
| estado_civil | Estado Civil | Select |  Solteiro(a) Casado(a) Divorciado(a) Viúvo(a) União Estável |  |  |
| profissao | Profissão | Data |  |  |  |
| representante | Representante Legal | Data |  |  |  |
| cpf_representante | CPF do Representante | Data |  |  |  |
| cargo_representante | Cargo | Data |  |  |  |
| nacionalidade_pj | Nacionalidade do Representante | Data |  |  |  |
| contacts | Contatos | Table | Client Contact |  |  |
| addresses | Endereços | Table | Client Address |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Court Cost

**Meta:** autoname=`format:CUST-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| tipo | Tipo | Select | Taxa Judicial Perícia Certidão Deslocamento Cópia/Impress... | ✓ |  |
| descricao | Descrição | Data |  | ✓ |  |
| status | Status | Select | Pendente Pago Repassado Cancelado |  |  |
| valor | Valor | Currency |  | ✓ |  |
| data_pagamento | Data de Legal Payment | Date |  |  |  |
| repassar_cliente | Repassar ao Client | Check |  |  |  |
| data_repasse | Data de Repasse | Date |  |  |  |
| forma_pagamento | Forma de Legal Payment | Select | PIX TED Boleto Dinheiro Cartão |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| observacoes | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Deadline

**Meta:** autoname=`format:PRAZO-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| data_prazo | Data do Prazo | Date |  | ✓ |  |
| status | Status | Select | Pendente Concluído Vencido |  |  |
| descricao | Descrição | Small Text |  | ✓ |  |
| prioridade | Prioridade | Select | Alta Média Baixa |  |  |
| responsavel | Responsável | Link | User |  |  |
| dias_notificacao | Notificar com antecedência (dias) | Int |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Document Kit

**Meta:** autoname=`field:titulo` · naming_rule=`By fieldname` · title_field=`titulo` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Título | Data |  | ✓ | ✓ |
| descricao | Descrição | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| templates | Templates | Table | Document Kit Item | ✓ |  |

### Document Template

**Meta:** autoname=`field:titulo` · naming_rule=`By fieldname` · title_field=`titulo` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Titulo | Data |  | ✓ | ✓ |
| tipo_documento | Tipo de Documento | Select | Contrato Declaracao Recibo Carta Ficha de Atendimento Outro | ✓ |  |
| descricao | Descricao | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| arquivo | Arquivo Template (.docx) | Attach |  | ✓ |  |
| ver_placeholders | Ver Placeholders Disponíveis | Button |  |  |  |

### Fee Agreement

**Meta:** autoname=`format:ACOR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| modo_honorarios | Modo | Select | Honorários Diretos Acordo com Divisão | ✓ |  |
| status | Status | Select | Vigente Encerrado Cancelado Quitado |  |  |
| valor_total_do_acordo | Valor Total do Acordo | Currency |  |  |  |
| percentual_advogada | Percentual Advogada (%) | Percent |  |  |  |
| valor_fixo_de_honorarios | Valor Fixo de Honorários | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| billing_type | Tipo de cobrança | Select | Valor fixo Percentual do acordo Percentual da causa Misto | ✓ |  |
| percentual_cliente | Percentual Client | Percent |  |  |  |
| valor_cliente | Valor Client | Currency |  |  |  |
| calculation_type | Tipo de cálculo | Select | Percentual Valor fixo |  |  |
| contingency_fee_pct | Percentual Sucumbência (%) | Percent |  |  |  |
| contingency_fee_amount | Honorários de Sucumbência | Currency |  |  |  |
| contingency_fee_status | Status da Sucumbência | Select | A definir Deferida Indeferida Paga |  |  |
| installment_count | Número de Parcelas | Int |  |  |  |
| data_primeira_parcela | Data Primeira Parcela | Date |  |  |  |
| valor_da_parcela | Valor da Parcela | Currency |  |  |  |
| gerar_parcelas | Gerar Parcelas | Button |  |  |  |
| fee_installments |  | Table | Fee Installment |  |  |
| total_advogada | Total Advogada | Currency |  |  |  |
| total_cliente | Total Client | Currency |  |  |  |
| remarks | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Hearing

**Meta:** autoname=`format:AUD-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| data_hora | Data e Hora | Datetime |  | ✓ |  |
| status_aud | Status | Select | Agendada Realizada Adiada Cancelada |  |  |
| tipo | Tipo | Select | Conciliação Instrução Julgamento Una | ✓ |  |
| modalidade | Modalidade | Select | Presencial Virtual Híbrida |  |  |
| link_virtual | Link da Audiência Virtual | Data | URL |  |  |
| court_branch | Court Branch | Link | Court Branch |  |  |
| resultado | Resultado | Select |  Realizada Adiada Acordo Sem acordo |  |  |
| observacoes | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Legal Case

**Meta:** autoname=`format:SERV-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| client | Client | Link | Client | ✓ |  |
| tipo | Tipo | Select | Processo Judicial Consultoria Contrato Diligência Adminis... | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Em andamento Encerrado Suspenso Arquivado |  |  |
| case_phase | Case Phase | Link | Case Phase |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| numero_processo | Número do Processo | Data |  |  |  |
| numeracao_legada | Numeração legada (pré-CNJ) | Check |  |  |  |
| area | Área | Select |  Família Trabalhista Cível Criminal Previdenciário Admini... |  |  |
| court_branch_link | Court Branch | Link | Court Branch |  |  |
| court | Court | Link | Court |  |  |
| jurisdiction | Jurisdiction | Link | Jurisdiction |  |  |
| parte_contraria | Parte Contrária | Data |  |  |  |
| valor_causa | Valor da Causa | Currency |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Legal Payment

**Meta:** autoname=`format:PAG-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tipo_origem | Origem | Select | Honorários (Parcela) Atos Advocatícios |  |  |
| fee_agreement | Acordo | Link | Fee Agreement |  |  |
| service_record | Service Record | Link | Service Record |  |  |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client | ✓ |  |
| numero_parcela | Nº Parcela | Int |  |  |  |
| descricao | Descrição | Small Text |  |  |  |
| parcela_origem_id | ID Origem | Data |  |  | ✓ |
| sincronizado_em | Sincronizado em | Datetime |  |  |  |
| manual_override | Edição manual (não sincronizar) | Check |  |  |  |
| valor | Valor | Currency |  | ✓ |  |
| valor_recebido | Valor Recebido | Currency |  |  |  |
| data_vencimento | Vencimento | Date |  | ✓ |  |
| data_recebimento | Data de Recebimento | Date |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Cancelado Renegociado Repassado | ✓ |  |
| observacoes | Observações | Small Text |  |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| title | Título | Data |  |  |  |

### Legal Task

**Meta:** autoname=`format:TAR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case |  |  |
| client | Client | Link | Client |  |  |
| titulo | Descrição da Legal Task | Data |  | ✓ |  |
| status | Status | Select | Pendente Em Andamento Concluída Cancelada |  |  |
| prioridade | Prioridade | Select | Normal Alta Urgente |  |  |
| data_limite | Data Limite | Date |  |  |  |
| descricao | Descrição | Text Editor |  |  |  |
| responsavel | Responsável | Link | User |  |  |
| data_conclusao | Data de Conclusão | Date |  |  |  |
| title | Título | Data |  |  |  |

### Office Expense

**Meta:** autoname=`format:DESP-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| descricao | Descrição | Data |  | ✓ |  |
| categoria | Categoria | Select | Aluguel Energia Água Internet Telefone Software/Assinatur... | ✓ |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Pago Atrasado Cancelado |  |  |
| data_vencimento | Data de Vencimento | Date |  |  |  |
| data_pagamento | Data de Legal Payment | Date |  |  |  |
| forma_pagamento | Forma de Legal Payment | Select | PIX TED Boleto Dinheiro Cartão Débito Automático |  |  |
| recorrente | Despesa Recorrente | Check |  |  |  |
| frequencia | Frequência | Select | Mensal Bimestral Trimestral Semestral Anual |  |  |
| proximo_vencimento | Próximo Vencimento | Date |  |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| observacoes | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Service Record

**Meta:** autoname=`format:ATOS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| status | Status | Select | Em aberto Parcialmente cobrado Cobrado |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| acts |  | Table | Legal Act Item |  |  |
| total_pendente | Total Pendente | Currency |  |  |  |
| total_cobrado | Total Cobrado | Currency |  |  |  |
| total_geral | Total Geral | Currency |  |  |  |
| data_vencimento_cobranca | Vencimento da Cobrança | Date |  |  |  |
| last_payment | Último Legal Payment | Link | Legal Payment |  |  |
| gerar_cobranca | Sincronizar Cobrança | Button |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Time Entry

**Meta:** autoname=`format:HRS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| legal_case | Serviço | Link | Legal Case | ✓ |  |
| client | Client | Link | Client |  |  |
| data | Data | Date |  | ✓ |  |
| responsavel | Responsável | Link | User |  |  |
| hora_inicio | Hora Início | Time |  |  |  |
| hora_fim | Hora Fim | Time |  |  |  |
| duracao_minutos | Duração (min) | Int |  |  |  |
| duracao_horas | Duração (horas) | Float |  |  |  |
| atividade | Atividade | Data |  | ✓ |  |
| categoria | Categoria | Select | Estudo/Pesquisa Redação Audiência Reunião Deslocamento At... |  |  |
| descricao | Detalhes | Small Text |  |  |  |
| cobravel | Cobrável | Check |  |  |  |
| timer_display | Tempo Decorrido | HTML |  |  |  |
| timer_inicio | Início do Timer | Datetime |  |  |  |
| timer_ativo | Timer Ativo | Check |  |  |  |
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
| tipo | Tipo | Select | Residencial Comercial Correspondência Outro |  |  |
| cep | CEP | Data |  |  |  |
| logradouro | Logradouro | Data |  | ✓ |  |
| numero | Número | Data |  |  |  |
| complemento | Complemento | Data |  |  |  |
| bairro | Bairro | Data |  |  |  |
| cidade | Cidade | Data |  |  |  |
| estado | Estado | Select |  AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ... |  |  |
| principal | Endereço Principal | Check |  |  |  |

### Client Contact

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| nome | Nome | Data |  | ✓ |  |
| tipo | Tipo | Select | Principal Conjuge Responsável Outro |  |  |
| telefone | Telefone | Data |  |  |  |
| celular | Celular | Data |  |  |  |
| email | E-mail | Data | Email |  |  |
| observacao | Observação | Small Text |  |  |  |

### Document Kit Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| template | Template | Link | Document Template | ✓ |  |
| ordem | Ordem | Int |  |  |  |

### Fee Installment

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| vencimento | Vencimento | Date |  | ✓ |  |
| valor_total | Valor Total | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| contingency_amount | Valor Sucumbência | Currency |  |  |  |
| valor_cliente | Valor Client | Currency |  |  |  |
| description | Descrição | Small Text |  |  |  |
| parcela_origem_id | ID de Origem | Data |  |  |  |
| payment | Legal Payment | Link | Legal Payment |  |  |
| status | Status | Select | Pendente Vencido Recebido Repassado Cancelado |  |  |
| data_recebimento | Data de Recebimento | Date |  |  |  |
| data_repasse | Data de Repasse ao Client | Date |  |  |  |
| forma_recebimento | Forma de Recebimento | Select |  PIX TED Dinheiro Cartão Boleto |  |  |
| observacao | Observação | Small Text |  |  |  |

### Legal Act Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| data | Data | Date |  | ✓ |  |
| tipo | Tipo | Select | Inicial Audiência Defesa Diligência Consulta Contrato Adm... | ✓ |  |
| description | Descrição | Small Text |  |  |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Cobrado |  |  |
| payment | Legal Payment | Link | Legal Payment |  |  |

#### Single

### Office Settings

**Meta:** autoname=`Office Settings` · naming_rule=`Expression` · title_field=`` · istable=0 · issingle=1

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| razao_social | Razão Social | Data |  | ✓ |  |
| cnpj | CNPJ | Data |  |  |  |
| registro_sia | Registro SIA | Data |  |  |  |
| office_logo | Logo do Escritório | Attach Image |  |  |  |
| advogada | Advogada(o) Principal | Data |  | ✓ |  |
| oab | OAB | Data |  | ✓ |  |
| default_notify_days | Dias padrão de antecedência (prazos) | Int |  |  |  |
| endereco | Endereço Completo | Small Text |  | ✓ |  |
| bank_name | Banco | Data |  |  |  |
| bank_agency | Agência | Data |  |  |  |
| bank_account | Conta | Data |  |  |  |
| bank_pix | Chave PIX | Data |  |  |  |

### Grafo de links (resumo)

`Client` ← Legal Case, Legal Payment, Acordo, … · `Jurisdiction` ← Court Branch, Legal Case · `Legal Case` hub → Prazos, Hearing, Atos, Horas, Custas · `Acordo` → `Fee Installment` → Legal Payment · `Service Record` → `Legal Act Item` (`cobranca_id` Link Legal Payment) · Auxiliares: Jurisdiction, Court Branch, Court, Case Phase.

## 4. hooks.py

### fixtures
Workspace Advocacia; Notifications prazo/audiência; Custom Field Event `custom_source%`.

### app_include_js
- `/assets/advocacia/js/masks.js`
- `/assets/advocacia/js/documentos_placeholders.js`
- `/assets/advocacia/js/painel/utils.js … index.js (8 módulos)`
- `/assets/advocacia/js/list_nav.js`
- `/assets/advocacia/js/list_filters.js`
- `/assets/advocacia/js/cliente_from_servico.js`
- `/assets/advocacia/js/timer_global.js`

**Removidos:** `navegacao.js`, widget painel global, `servico_link.js` (label de Serviço em `legal_case_query` / `format_servico_link_label`).

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

- Globais (4), 12 list formatters, forms (acordo, servico, audiencia Híbrida).
- `painel.js` ~4100 linhas; CSS vars para charts.
- Calendários: `audiencia_calendar.js`, `controle_de_prazos_calendar.js`.

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

- **245** métodos em **36** arquivos.
- `bench --site advocacia.local run-tests --app advocacia`
- Última run (site dev): **245** testes, **OK** (jun/2026).

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
| 12 | Testes | ✅ | 221/221 OK |
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
| Suite 221/221 verde | ✅ |
| install-app site limpo | ⏳ recomendado pré go-live |

**Conclusão:** código e testes **prontos para produção**; validar reinstall limpo e smoke manual do painel/sidebar antes do go-live.
