# CODEBASE — App Advocacia (Frappe v16)

> Gerado em **2026-06-02** — re-audit pós-UX (títulos, list views, sidebar, painel). Branch **`frappe-v16`**. Frappe puro, **sem ERPNext**.

> **HEAD:** `9d0c473 2026-06-02 14:15:51 +0000 fix: restore payment origin column and add client ID badge`

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | advocacia |
| Versão | 0.6.0 (`pyproject.toml`) |
| Framework | Frappe v16.19.0 |
| Licença | MIT |
| Branch | frappe-v16 |
| Remote | git@github.com:ctomazini/advocacia.git |
| Site dev | advocacia.local (porta 8000) |
| Linhas Python | ~9967 |
| Linhas JavaScript | ~6720 |
| Métodos de teste | 221 |
| DocTypes | 24 (todos `custom: 0`) |
| Script Reports | 6 |

**Propósito:** LegalTech BR — clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas, registro de horas, painel, documentos `.docx`.

**Deps:** `docxtpl>=0.18.0`; jquery.inputmask (Frappe).

### 1.1 Entregas recentes (jun/2026)

| Área | Mudança |
| --- | --- |
| **Naming** | `format:PREFIX-{YYYY}-{####}` + `naming_rule: Expression` |
| **Títulos** | `titulos.py`: `{ID} — {descritor}`; `show_title_field_in_link` |
| **List views** | 12 `*_list.js` com `hide_name_column` e `states` |
| **Cliente** | `title_field=nome`; badge ID em `cliente_list.js` |
| **Pagamento** | Coluna Origem (`tipo_origem` + link Acordo/Registro) |
| **Painel** | Nomes legíveis via `painel/`; `painel.js` ~4100 linhas |
| **Sidebar** | `collapsible: 1` nas seções (fix scroll Frappe v16) |

**Commits recentes:**
```text
9d0c473 fix: restore payment origin column and add client ID badge
81f7fca fix: enforce ID-prefixed titles and simplify list columns
55a90ad fix: Section Breaks collapsíveis na sidebar Advocacia
13b5ab1 fix: painel exibe nomes legíveis em vez de IDs
bed6850 feat: título visível no topo do form com composição automática
54d3a96 fix: padronizar autoname com ano em todos os DocTypes
a3dd069 chore: add demo seed utility for dev testing
63923a0 feat: ID-based editable titles with show_title_field_in_link across all doctypes
979cbcb feat: homogeneous title pattern (ID + descriptive title) across all doctypes
8291317 feat: show descriptive titles instead of codes in links, forms and list views
c62bcf9 fix: allow Registro de Horas without duration and add save-and-start timer
8e18133 fix: resolve Registro de Horas 403 (timer sync) and make timer loop resilient to permission errors
```

## 2. Árvore de Arquivos (anotada)

```text
advocacia/
├── CODEBASE.md, README.md, pyproject.toml
└── advocacia/
    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/
    ├── fixtures/, workspace_sidebar/advocacia.json
    ├── public/js/ (4: masks, list_nav, cliente_from_servico, timer_global)
    └── advocacia/
        ├── validators.py, titulos.py, painel_api.py (facade)
        ├── painel/ (kpis, financeiro, prazos, timeline, _helpers)
        ├── documentos.py, financeiro.py, tasks.py, notificacoes.py, calendar_sync.py
        ├── setup/ (install, sidebar, workspace, reports, translations, seed_demo)
        ├── tests/ (33 arquivos), doctype/ (24), page/painel/, report/ (6), workspace/
```

## 3. Mapa de DocTypes (24)

Colunas: `fieldname` | label | fieldtype | options | reqd | unique. Section/Column/Tab breaks omitidos.

#### Standalone / transacionais

### Acordo de Honorarios Processuais

**Meta:** autoname=`format:ACOR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| modo_honorarios | Modo | Select | Honorários Diretos Acordo com Divisão | ✓ |  |
| servico | Serviço | Link | Servico | ✓ |  |
| title | Título | Data |  |  |  |
| cliente | Cliente | Link | Cliente |  |  |
| status | Status | Select | Vigente Encerrado Cancelado Quitado |  |  |
| valor_total_do_acordo | Valor Total do Acordo | Currency |  |  |  |
| percentual_advogada | Percentual Advogada (%) | Percent |  |  |  |
| valor_fixo_de_honorarios | Valor Fixo de Honorários | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| tipo_de_cobrança | Tipo de cobrança | Select | Valor fixo Percentual do acordo Percentual da causa Misto | ✓ |  |
| percentual_cliente | Percentual Cliente | Percent |  |  |  |
| valor_cliente | Valor Cliente | Currency |  |  |  |
| tipo_de_cálculo | Tipo de cálculo | Select | Percentual Valor fixo |  |  |
| percentual_sucumbência | Percentual Sucumbência (%) | Percent |  |  |  |
| honorários_de_sucumbência | Honorários de Sucumbência | Currency |  |  |  |
| status_da_sucumbência | Status da Sucumbência | Select | A definir Deferida Indeferida Paga |  |  |
| número_de_parcelas | Número de Parcelas | Int |  |  |  |
| data_primeira_parcela | Data Primeira Parcela | Date |  |  |  |
| valor_da_parcela | Valor da Parcela | Currency |  |  |  |
| gerar_parcelas | Gerar Parcelas | Button |  |  |  |
| parcelas |  | Table | Parcela de Honorarios |  |  |
| total_advogada | Total Advogada | Currency |  |  |  |
| total_cliente | Total Cliente | Currency |  |  |  |
| observações | Observações | Text Editor |  |  |  |

### Audiencia

**Meta:** autoname=`format:AUD-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| data_hora | Data e Hora | Datetime |  | ✓ |  |
| status_aud | Status | Select | Agendada Realizada Adiada Cancelada |  |  |
| tipo | Tipo | Select | Conciliação Instrução Julgamento Una | ✓ |  |
| modalidade | Modalidade | Select | Presencial Virtual Híbrida |  |  |
| link_virtual | Link da Audiência Virtual | Data | URL |  |  |
| local_vara | Vara | Link | Vara |  |  |
| resultado | Resultado | Select |  Realizada Adiada Acordo Sem acordo |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Cliente

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
| contatos | Contatos | Table | Contato Cliente |  |  |
| enderecos | Endereços | Table | Endereco Cliente |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Comunicacao

**Meta:** autoname=`format:COM-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico |  |  |
| cliente | Cliente | Link | Cliente | ✓ |  |
| data | Data | Datetime |  | ✓ |  |
| tipo | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtua... | ✓ |  |
| assunto | Assunto | Data |  | ✓ |  |
| resumo | Resumo | Text Editor |  |  |  |
| proximos_passos | Próximos Passos | Small Text |  |  |  |
| gerar_tarefa | Gerar Tarefa | Check |  |  |  |
| tarefa | Tarefa Gerada | Link | Tarefa |  |  |
| title | Título | Data |  |  |  |

### Controle de Prazos

**Meta:** autoname=`format:PRAZO-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| data_prazo | Data do Prazo | Date |  | ✓ |  |
| status | Status | Select | Pendente Concluído Vencido |  |  |
| descricao | Descrição | Small Text |  | ✓ |  |
| prioridade | Prioridade | Select | Alta Média Baixa |  |  |
| responsavel | Responsável | Link | User |  |  |
| dias_notificacao | Notificar com antecedência (dias) | Int |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Custa Processual

**Meta:** autoname=`format:CUST-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| tipo | Tipo | Select | Taxa Judicial Perícia Certidão Deslocamento Cópia/Impress... | ✓ |  |
| descricao | Descrição | Data |  | ✓ |  |
| status | Status | Select | Pendente Pago Repassado Cancelado |  |  |
| valor | Valor | Currency |  | ✓ |  |
| data_pagamento | Data de Pagamento | Date |  |  |  |
| repassar_cliente | Repassar ao Cliente | Check |  |  |  |
| data_repasse | Data de Repasse | Date |  |  |  |
| forma_pagamento | Forma de Pagamento | Select | PIX TED Boleto Dinheiro Cartão |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| observacoes | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Despesa do Escritorio

**Meta:** autoname=`format:DESP-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| descricao | Descrição | Data |  | ✓ |  |
| categoria | Categoria | Select | Aluguel Energia Água Internet Telefone Software/Assinatur... | ✓ |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Pago Atrasado Cancelado |  |  |
| data_vencimento | Data de Vencimento | Date |  |  |  |
| data_pagamento | Data de Pagamento | Date |  |  |  |
| forma_pagamento | Forma de Pagamento | Select | PIX TED Boleto Dinheiro Cartão Débito Automático |  |  |
| recorrente | Despesa Recorrente | Check |  |  |  |
| frequencia | Frequência | Select | Mensal Bimestral Trimestral Semestral Anual |  |  |
| proximo_vencimento | Próximo Vencimento | Date |  |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| observacoes | Observações | Small Text |  |  |  |
| title | Título | Data |  |  |  |

### Kit de Documentos

**Meta:** autoname=`field:titulo` · naming_rule=`By fieldname` · title_field=`titulo` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Título | Data |  | ✓ | ✓ |
| descricao | Descrição | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| templates | Templates | Table | Kit Documento Item | ✓ |  |

### Pagamento

**Meta:** autoname=`format:PAG-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tipo_origem | Origem | Select | Honorários (Parcela) Atos Advocatícios |  |  |
| acordo | Acordo | Link | Acordo de Honorarios Processuais |  |  |
| registro_atos | Registro de Atos | Link | Registro de Atos |  |  |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente | ✓ |  |
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

### Registro de Atos

**Meta:** autoname=`format:ATOS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| title | Título | Data |  |  |  |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| status | Status | Select | Em aberto Parcialmente cobrado Cobrado |  |  |
| atos |  | Table | Ato Advocaticio |  |  |
| total_pendente | Total Pendente | Currency |  |  |  |
| total_cobrado | Total Cobrado | Currency |  |  |  |
| total_geral | Total Geral | Currency |  |  |  |
| data_vencimento_cobranca | Vencimento da Cobrança | Date |  |  |  |
| ultimo_pagamento | Último Pagamento | Link | Pagamento |  |  |
| gerar_cobranca | Sincronizar Cobrança | Button |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Registro de Horas

**Meta:** autoname=`format:HRS-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
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

### Servico

**Meta:** autoname=`format:SERV-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| fase_processual | Fase Processual | Link | Fase Processual |  |  |
| tribunal | Tribunal | Link | Tribunal |  |  |
| cliente | Cliente | Link | Cliente | ✓ |  |
| tipo | Tipo | Select | Processo Judicial Consultoria Contrato Diligência Adminis... | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Em andamento Encerrado Suspenso Arquivado |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| numero_processo | Número do Processo | Data |  |  |  |
| numeracao_legada | Numeração legada (pré-CNJ) | Check |  |  |  |
| area | Área | Select |  Família Trabalhista Cível Criminal Previdenciário Admini... |  |  |
| vara | Vara | Link | Vara |  |  |
| comarca | Comarca | Link | Comarca |  |  |
| parte_contraria | Parte Contrária | Data |  |  |  |
| valor_causa | Valor da Causa | Currency |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Tarefa

**Meta:** autoname=`format:TAR-{YYYY}-{####}` · naming_rule=`Expression` · title_field=`title` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico |  |  |
| cliente | Cliente | Link | Cliente |  |  |
| titulo | Descrição da Tarefa | Data |  | ✓ |  |
| status | Status | Select | Pendente Em Andamento Concluída Cancelada |  |  |
| prioridade | Prioridade | Select | Normal Alta Urgente |  |  |
| data_limite | Data Limite | Date |  |  |  |
| descricao | Descrição | Text Editor |  |  |  |
| responsavel | Responsável | Link | User |  |  |
| data_conclusao | Data de Conclusão | Date |  |  |  |
| title | Título | Data |  |  |  |

### Template Documento

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

### Comarca

**Meta:** autoname=`field:comarca_name` · naming_rule=`` · title_field=`comarca_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| comarca_name | Nome da Comarca | Data |  | ✓ | ✓ |
| uf | UF | Select | AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ ... | ✓ |  |
| city | Cidade | Data |  |  |  |

### Fase Processual

**Meta:** autoname=`field:phase_name` · naming_rule=`` · title_field=`phase_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| phase_name | Nome da Fase | Data |  | ✓ | ✓ |
| sort_order | Ordem | Int |  |  |  |

### Tribunal

**Meta:** autoname=`field:tribunal_name` · naming_rule=`` · title_field=`tribunal_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tribunal_name | Nome do Tribunal | Data |  | ✓ | ✓ |
| abbreviation | Sigla | Data |  | ✓ | ✓ |
| jurisdiction | Esfera | Select | Estadual Federal Trabalho Superior Militar Eleitoral | ✓ |  |

### Vara

**Meta:** autoname=`field:vara_name` · naming_rule=`` · title_field=`vara_name` · istable=0 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| vara_name | Nome da Vara | Data |  | ✓ | ✓ |
| comarca | Comarca | Link | Comarca | ✓ |  |
| court_type | Tipo | Select | Cível Criminal Família Trabalho Federal Juizado Especial ... |  |  |

#### Child tables

### Ato Advocaticio

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| cobranca_id | Pagamento | Link | Pagamento |  |  |
| data | Data | Date |  | ✓ |  |
| tipo | Tipo | Select | Inicial Audiência Defesa Diligência Consulta Contrato Adm... | ✓ |  |
| descrição | Descrição | Small Text |  |  |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Cobrado |  |  |

### Contato Cliente

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| nome | Nome | Data |  | ✓ |  |
| tipo | Tipo | Select | Principal Conjuge Responsável Outro |  |  |
| telefone | Telefone | Data |  |  |  |
| celular | Celular | Data |  |  |  |
| email | E-mail | Data | Email |  |  |
| observacao | Observação | Small Text |  |  |  |

### Endereco Cliente

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

### Kit Documento Item

**Meta:** autoname=`None` · naming_rule=`` · title_field=`` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| template | Template | Link | Template Documento | ✓ |  |
| ordem | Ordem | Int |  |  |  |

### Parcela de Honorarios

**Meta:** autoname=`None` · naming_rule=`` · title_field=`None` · istable=1 · issingle=0

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| parcela_origem_id | ID de Origem | Data |  |  |  |
| pagamento | Pagamento | Link | Pagamento |  |  |
| data_recebimento | Data de Recebimento | Date |  |  |  |
| data_repasse | Data de Repasse ao Cliente | Date |  |  |  |
| forma_recebimento | Forma de Recebimento | Select |  PIX TED Dinheiro Cartão Boleto |  |  |
| observacao | Observação | Small Text |  |  |  |
| vencimento | Vencimento | Date |  | ✓ |  |
| valor_total | Valor Total | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| valor_sucumbência | Valor Sucumbência | Currency |  |  |  |
| valor_cliente | Valor Cliente | Currency |  |  |  |
| descrição | Descrição | Small Text |  |  |  |
| status | Status | Select | Pendente Vencido Recebido Repassado Cancelado |  |  |

#### Single

### Configuracao do Escritorio

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

`Cliente` ← Servico, Pagamento, Acordo, … · `Comarca` ← Vara, Servico · `Servico` hub → Prazos, Audiencia, Atos, Horas, Custas · `Acordo` → `Parcela de Honorarios` → Pagamento · `Registro de Atos` → `Ato Advocaticio` (`cobranca_id` Link Pagamento) · Auxiliares: Comarca, Vara, Tribunal, Fase Processual.

## 4. hooks.py

### fixtures
Workspace Advocacia; Notifications prazo/audiência; Custom Field Event `custom_source%`.

### app_include_js (4)
- `/assets/advocacia/js/masks.js`
- `/assets/advocacia/js/list_nav.js`
- `/assets/advocacia/js/cliente_from_servico.js`
- `/assets/advocacia/js/timer_global.js`

**Removidos:** `navegacao.js`, widget painel global, `servico_link.js` (label de Serviço em `servico_query` / `format_servico_link_label`).

### doc_events

| DocType | Evento | Handler |
| --- | --- | --- |
| Acordo de Honorarios Processuais | on_update | financeiro.sincronizar_pagamentos_hook |
| Parcela de Honorarios | on_update | tasks.on_parcela_update |
| Pagamento | on_update | financeiro.processar_pagamento_on_update |
| Pagamento | on_trash | financeiro.on_pagamento_trash |
| Audiencia | after_insert / on_update | calendar_sync.sync_audiencia_to_event |
| Controle de Prazos | after_insert / on_update | calendar_sync.sync_prazo_to_event |

### scheduler_events
- **daily:** verificar_parcelas_vencidas, verificar_despesas_vencidas, notificar_parcelas_vencidas, notificar_audiencias_hoje, notificar_prazos_diario
- **weekly:** verificar_status_servicos

### after_migrate
reinstalar_istable → after_install → event fields → translations → sidebar → reports → workspace

## 5. API whitelisted

| Função | Módulo | Permissão | Chamador |
| --- | --- | --- | --- |
| get_painel_data | painel_api → painel.get | Servico read | painel.js xcall |
| marcar_parcela_recebida | painel_api → painel.financeiro | Pagamento write | painel.js |
| servico_query | servico | query | Link Servico |
| gerar_documento_servico / em_lote | documentos | Servico read/write | servico.js |
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

Status Pagamento: Pendente, Vencido, Recebido, Cancelado, Renegociado, Repassado.

## 10. Fixtures / Workspace / Sidebar

- 26 links sidebar ↔ workspace.
- Seções com `collapsible: 1` (Frappe v16).

## 11. Testes

- **221** métodos em **33** arquivos.
- `bench --site advocacia.local run-tests --app advocacia`
- Última run (site dev): **221** testes, **OK** (jun/2026).

## 12. Integrações

- calendar_sync → Event; documentos → docxtpl; Configuracao do Escritorio (Single).

## 13. Backlog consciente

1. Chart.js → frappe.ui.Chart
2. Fieldnames EN auxiliares (`city`, `phase_name`)
3. sql → qb no painel
4. Modularizar `painel.js`

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
| 10 | Hooks | ✅ | Pagamento handler único; schedulers |
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
