# CODEBASE — App Advocacia (Frappe v16)

> Gerado em **2026-06-02**, atualizado **2026-06-07** (filtros, connections, E2E). Branch **`frappe-v16`**. Frappe puro, **sem ERPNext**.

> **HEAD:** `cf33fc5 test: add Playwright E2E script for Advocacia UI flow`

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | advocacia |
| Versão | 0.7.0 (`pyproject.toml`) |
| Framework | Frappe v16.19.0 |
| Licença | MIT |
| Branch | frappe-v16 |
| Remote | git@github.com:ctomazini/advocacia.git |
| Site dev | advocacia.local (porta 8000) |
| Linhas Python | ~9967 |
| Linhas JavaScript | ~6720 |
| Métodos de teste | 230 (`run-tests --app advocacia`) |
| DocTypes | 24 (todos `custom: 0`) |
| Script Reports | 6 |

**Propósito:** LegalTech BR — clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas, registro de horas, painel, documentos `.docx`.

**Deps:** `docxtpl>=0.18.0`; jquery.inputmask (Frappe).

### 1.1 Entregas recentes (jun/2026)

| Área | Mudança |
| --- | --- |
| **Filtros de lista** | `in_standard_filter` em 17 DocTypes; `list_filters.js` + `list_filters.css` (desktop sempre visível, mobile no botão ⇅) |
| **Connections** | `list_nav.js`: clique em count/link abre lista filtrada pelo documento pai |
| **Painel** | Frontend modular `public/js/painel/`; soft refresh (período/limites sem reload total) |
| **Naming / títulos** | `format:PREFIX-{YYYY}-{####}`; `titulos.py` → `{ID} — {descritor}` |
| **List views** | 12 `*_list.js`; Legal Payment coluna Origem; Client badge ID |
| **E2E UI** | `tests/e2e/playwright_flow.py` — marcador `_PW_E2E_`, cleanup automático |
| **Sidebar** | `collapsible: 1` (fix scroll Frappe v16) |

**Commits recentes:**
```text
cf33fc5 test: add Playwright E2E script for Advocacia UI flow
a2d9305 fix: painel soft refresh for period and list limit filters
7dcd549 feat: responsive list filter bar for mobile and desktop
26edc2b fix: navigate form connections to filtered list views
4cd02fe feat: expand dashboard connections and standard list filters on DocTypes
18783a7 docs: phase 2 audit suite, manual_usuario.md and REGRAS_ADVOCACIA v0.7.0
36f57b3 refactor: split painel.js into modular JS files and page CSS
```

## 2. Árvore de Arquivos (anotada)

```text
advocacia/
├── CODEBASE.md, README.md, pyproject.toml
└── advocacia/
    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/
    ├── fixtures/, workspace_sidebar/advocacia.json
    ├── public/js/ (masks, list_nav, list_filters, cliente_from_servico, timer_global, painel/*)
    ├── public/css/ (list_filters.css, painel.css)
    └── advocacia/
        ├── validators.py, titulos.py, painel_api.py (facade)
        ├── painel/ (kpis, financeiro, prazos, timeline, _helpers)
        ├── documentos.py, financeiro.py, tasks.py, notificacoes.py, calendar_sync.py
        ├── setup/ (install, sidebar, workspace, reports, translations, seed_demo)
        ├── tests/ (35 arquivos + e2e/), doctype/ (24), page/painel/, report/ (6), workspace/
        └── docs/ (manual, audit_*, e2e_playwright.md, README índice)
```

## 3. Mapa de DocTypes (24)

Colunas: `fieldname` | label | fieldtype | options | reqd | unique. Section/Column/Tab breaks omitidos.

#### Standalone / transacionais

### Fee Agreement

**Meta:** autoname=`format:ACOR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| modo_honorarios | Modo | Select | Honorários Diretos Acordo com Divisão | ✓ |  |
| servico | Serviço | Link | Legal Case | ✓ |  |
| title | Título | Data |  |  |  |
| cliente | Client | Link | Client |  |  |
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
| parcelas |  | Table | Fee Installment |  |  |
| total_advogada | Total Advogada | Currency |  |  |  |
| total_cliente | Total Client | Currency |  |  |  |
| remarks | Observações | Text Editor |  |  |  |

### Hearing

**Meta:** autoname=`format:AUD-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client |  |  |
| data_hora | Data e Hora | Datetime |  | ✓ |  |
| status_aud | Status | Select | Agendada Realizada Adiada Cancelada |  |  |
| tipo | Tipo | Select | Conciliação Instrução Julgamento Una | ✓ |  |
| modalidade | Modalidade | Select | Presencial Virtual Híbrida |  |  |
| link_virtual | Link da Audiência Virtual | Data | URL |  |  |
| local_vara | Court Branch | Link | Court Branch |  |  |
| resultado | Resultado | Select |  Realizada Adiada Acordo Sem acordo |  |  |
| observacoes | Observações | Text Editor |  |  |  |

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
| contatos | Contatos | Table | Client Contact |  |  |
| enderecos | Endereços | Table | Client Address |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Case Communication

**Meta:** autoname=`format:COM-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Legal Case |  |  |
| cliente | Client | Link | Client | ✓ |  |
| data | Data | Datetime |  | ✓ |  |
| tipo | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtua... | ✓ |  |
| assunto | Assunto | Data |  | ✓ |  |
| resumo | Resumo | Text Editor |  |  |  |
| proximos_passos | Próximos Passos | Small Text |  |  |  |
| gerar_tarefa | Gerar Legal Task | Check |  |  |  |
| tarefa | Legal Task Gerada | Link | Legal Task |  |  |
| title | Título | Data |  |  |  |

### Deadline

**Meta:** autoname=`format:PRAZO-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client |  |  |
| data_prazo | Data do Prazo | Date |  | ✓ |  |
| status | Status | Select | Pendente Concluído Vencido |  |  |
| descricao | Descrição | Small Text |  | ✓ |  |
| prioridade | Prioridade | Select | Alta Média Baixa |  |  |
| responsavel | Responsável | Link | User |  |  |
| dias_notificacao | Notificar com antecedência (dias) | Int |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Court Cost

**Meta:** autoname=`format:CUST-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client |  |  |
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

### Document Kit

**Meta:** autoname=`field:titulo` · naming_rule=`By fieldname` · title_field=`titulo` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Título | Data |  | ✓ | ✓ |
| descricao | Descrição | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| templates | Templates | Table | Document Kit Item | ✓ |  |

### Legal Payment

**Meta:** autoname=`format:PAG-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tipo_origem | Origem | Select | Honorários (Parcela) Atos Advocatícios |  |  |
| acordo | Acordo | Link | Fee Agreement |  |  |
| registro_atos | Service Record | Link | Service Record |  |  |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client | ✓ |  |
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

### Service Record

**Meta:** autoname=`format:ATOS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| status | Status | Select | Em aberto Parcialmente cobrado Cobrado |  |  |
| atos |  | Table | Legal Act Item |  |  |
| total_pendente | Total Pendente | Currency |  |  |  |
| total_cobrado | Total Cobrado | Currency |  |  |  |
| total_geral | Total Geral | Currency |  |  |  |
| data_vencimento_cobranca | Vencimento da Cobrança | Date |  |  |  |
| ultimo_pagamento | Último Legal Payment | Link | Legal Payment |  |  |
| gerar_cobranca | Sincronizar Cobrança | Button |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Time Entry

**Meta:** autoname=`format:HRS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Legal Case | ✓ |  |
| cliente | Client | Link | Client |  |  |
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

### Legal Case

**Meta:** autoname=`format:SERV-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| fase_processual | Case Phase | Link | Case Phase |  |  |
| tribunal | Court | Link | Court |  |  |
| cliente | Client | Link | Client | ✓ |  |
| tipo | Tipo | Select | Processo Judicial Consultoria Contrato Diligência Adminis... | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Em andamento Encerrado Suspenso Arquivado |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| numero_processo | Número do Processo | Data |  |  |  |
| numeracao_legada | Numeração legada (pré-CNJ) | Check |  |  |  |
| area | Área | Select |  Família Trabalhista Cível Criminal Previdenciário Admini... |  |  |
| vara | Court Branch | Link | Court Branch |  |  |
| comarca | Jurisdiction | Link | Jurisdiction |  |  |
| parte_contraria | Parte Contrária | Data |  |  |  |
| valor_causa | Valor da Causa | Currency |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Legal Task

**Meta:** autoname=`format:TAR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Legal Case |  |  |
| cliente | Client | Link | Client |  |  |
| titulo | Descrição da Legal Task | Data |  | ✓ |  |
| status | Status | Select | Pendente Em Andamento Concluída Cancelada |  |  |
| prioridade | Prioridade | Select | Normal Alta Urgente |  |  |
| data_limite | Data Limite | Date |  |  |  |
| descricao | Descrição | Text Editor |  |  |  |
| responsavel | Responsável | Link | User |  |  |
| data_conclusao | Data de Conclusão | Date |  |  |  |
| title | Título | Data |  |  |  |

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

#### Auxiliares (cadastro rígido)

### Jurisdiction

**Meta:** autoname=`field:jurisdiction_name` · naming_rule=`` · title_field=`jurisdiction_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| jurisdiction_name | Nome da Jurisdiction | Data |  | ✓ | ✓ |
| uf | UF | Select | AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ ... | ✓ |  |
| city | Cidade | Data |  |  |  |

### Case Phase

**Meta:** autoname=`field:case_phase_name` · naming_rule=`` · title_field=`case_phase_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| case_phase_name | Nome da Fase | Data |  | ✓ | ✓ |
| sort_order | Ordem | Int |  |  |  |

### Court

**Meta:** autoname=`field:court_name` · naming_rule=`` · title_field=`court_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| court_name | Nome do Court | Data |  | ✓ | ✓ |
| abbreviation | Sigla | Data |  | ✓ | ✓ |
| jurisdiction | Esfera | Select | Estadual Federal Trabalho Superior Militar Eleitoral | ✓ |  |

### Court Branch

**Meta:** autoname=`field:court_branch_name` · naming_rule=`` · title_field=`court_branch_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| court_branch_name | Nome da Court Branch | Data |  | ✓ | ✓ |
| comarca | Jurisdiction | Link | Jurisdiction | ✓ |  |
| court_type | Tipo | Select | Cível Criminal Família Trabalho Federal Juizado Especial ... |  |  |

#### Child tables

### Legal Act Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| cobranca_id | Legal Payment | Link | Legal Payment |  |  |
| data | Data | Date |  | ✓ |  |
| tipo | Tipo | Select | Inicial Audiência Defesa Diligência Consulta Contrato Adm... | ✓ |  |
| description | Descrição | Small Text |  |  |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Cobrado |  |  |

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
| parcela_origem_id | ID de Origem | Data |  |  |  |
| pagamento | Legal Payment | Link | Legal Payment |  |  |
| data_recebimento | Data de Recebimento | Date |  |  |  |
| data_repasse | Data de Repasse ao Client | Date |  |  |  |
| forma_recebimento | Forma de Recebimento | Select |  PIX TED Dinheiro Cartão Boleto |  |  |
| observacao | Observação | Small Text |  |  |  |
| vencimento | Vencimento | Date |  | ✓ |  |
| valor_total | Valor Total | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| contingency_amount | Valor Sucumbência | Currency |  |  |  |
| valor_cliente | Valor Client | Currency |  |  |  |
| description | Descrição | Small Text |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Repassado Cancelado |  |  |

#### Single

### Office Settings

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=0 · issingle=1

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| razao_social | Razão Social | Data |  | ✓ |  |
| cnpj | CNPJ | Data |  |  |  |
| registro_sia | Registro SIA | Data |  |  |  |
| advogada | Advogada(o) Principal | Data |  | ✓ |  |
| oab | OAB | Data |  | ✓ |  |
| endereco | Endereço Completo | Small Text |  | ✓ |  |

### Grafo de links (resumo)

`Client` ← Legal Case, Legal Payment, Acordo, … · `Jurisdiction` ← Court Branch, Legal Case · `Legal Case` hub → Prazos, Hearing, Atos, Horas, Custas · `Acordo` → `Fee Installment` → Legal Payment · `Service Record` → `Legal Act Item` (`cobranca_id` Link Legal Payment) · Auxiliares: Jurisdiction, Court Branch, Court, Case Phase.

## 4. hooks.py

### fixtures
Workspace Advocacia; Notifications prazo/audiência; Custom Field Event `custom_source%`.

### app_include_css (1)
- `/assets/advocacia/css/list_filters.css`

### app_include_js (11)
- `/assets/advocacia/js/masks.js`
- `/assets/advocacia/js/painel/utils.js` … `index.js` (7 módulos painel)
- `/assets/advocacia/js/list_nav.js`
- `/assets/advocacia/js/list_filters.js`
- `/assets/advocacia/js/cliente_from_servico.js`
- `/assets/advocacia/js/timer_global.js`

**Removidos:** `navegacao.js`, widget painel global, `servico_link.js`.

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
| servico_query | servico | query | Link Legal Case |
| gerar_documento_servico / em_lote | documentos | Legal Case read/write | servico.js |
| get_kits_disponiveis | documentos | read | servico.js |
| get_placeholders_referencia | documentos | Template read | template_documento.js |
| registrar_recebimento/repasse | parcela | write | form |
| concluir | tarefa | write | tarefa.js |
| timer APIs | registro_de_horas | write | timer_global.js |
| get_events | audiencia/prazos | calendar read | *_calendar.js |
| gerar_proxima_despesa | despesa | create | form |
| financeiro sync | financeiro | has_permission | hooks |


**xcall:** `advocacia.advocacia.painel_api.get_painel_data` (facade — não alterar no JS).

## 6. Schedulers

Ver §4 (`tasks.py`, `notificacoes.py`). Sem `commit()` em request/scheduler.

## 7. Client JS

- **Globais:** masks, list_nav, list_filters, cliente_from_servico, timer_global.
- **Painel:** 7 módulos em `public/js/painel/` + shell `page/painel/painel.js` (13 linhas).
- **Listas:** 12 `*_list.js`; `in_standard_filter` em Link/Select/Date dos transacionais.
- **Connections:** `list_nav.js` intercepta cliques no dashboard do form → `frappe.set_route("List", doctype, filters)`.
- **Filtros responsivos:** `list_filters.js` patch em `BaseList.setup_filter_area` — desktop barra visível; mobile ⇅.
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

- **230** métodos em **35** arquivos `test_*.py` (+ `tests/e2e/` manual).
- `bench --site advocacia.local run-tests --app advocacia`
- Última run (site dev): **230/230 OK** (jun/2026).
- E2E browser: `tests/e2e/playwright_flow.py` — ver `advocacia/docs/e2e_playwright.md`.

## 12. Integrações

- calendar_sync → Event; documentos → docxtpl; Office Settings (Single).

## 13. Backlog consciente

1. Chart.js → frappe.ui.Chart
2. Fieldnames EN auxiliares (`city`, `case_phase_name`)
3. sql → qb no painel
4. `agent_api.py` jurídico (pós-deploy)
5. CI opcional com Playwright E2E

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
| 12 | Testes | ✅ | 230/230 OK |
| 13 | Reinstall limpo | ⏳ | Obrigatório pré go-live |
| 14 | Filtros / Connections UX | ✅ | list_filters + list_nav (jun/2026) |

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
| Suite 230/230 verde | ✅ |
| install-app site limpo | ⏳ recomendado pré go-live |

**Conclusão:** código e testes **prontos para produção**; validar reinstall limpo e smoke manual do painel/sidebar antes do go-live.
