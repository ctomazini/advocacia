# CODEBASE — App Advocacia (Frappe v16)

> Gerado em 2026-05-31 — re-audit final, branch `frappe-v16`. Frappe puro, sem ERPNext.

---

## 1. Visão Geral

| Item | Valor |
| --- | --- |
| Nome | advocacia |
| Versão | 0.6.0 |
| Framework | Frappe v16.19.0 |
| Licença | MIT |
| Módulo | Advocacia |
| Branch | frappe-v16 |
| Remote | git@github.com:ctomazini/advocacia.git |
| Site dev | advocacia.local (porta 8000) |
| Linhas Python | ~8423 |
| Linhas JavaScript | ~6622 |
| Testes | 195 |

**Propósito:** LegalTech BR — clientes, serviços, honorários, pagamentos, atos, prazos, audiências, despesas, painel, documentos docx.

**Deps:** docxtpl>=0.18.0; jquery.inputmask (Frappe).

---

## 2. Árvore de Arquivos (anotada)

```text
advocacia/
├── CODEBASE.md, README.md, pyproject.toml
└── advocacia/
    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/
    ├── fixtures/, workspace_sidebar/, public/js/ (5 arquivos, sem navegacao.js)
    └── advocacia/
        ├── validators.py, painel_api.py (facade), painel/ (kpis, financeiro, prazos, timeline, _helpers)
        ├── documentos.py, financeiro.py, tasks.py, notificacoes.py, calendar_sync.py
        ├── setup/, tests/, doctype/ (24), page/painel/, report/ (6), workspace/
```

---

## 3. Mapa de DocTypes (24)

Colunas: fieldname | label | fieldtype | options | reqd | unique

### Acordo de Honorarios Processuais

**Meta:** autoname=format:ACOR-{####}, naming_rule=Expression (old style), title_field=title

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| modo_honorarios | Modo | Select | Honorários Diretos Acordo com Divisão | ✓ |  |
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
| title | Título | Data |  |  |  |

### Ato Advocaticio

**Meta:** istable

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| data | Data | Date |  | ✓ |  |
| tipo | Tipo | Select | Inicial Audiência Defesa Diligência Consulta Contrato Administrativo Outro | ✓ |  |
| descrição | Descrição | Small Text |  |  |  |
| valor | Valor | Currency |  | ✓ |  |
| status | Status | Select | Pendente Cobrado |  |  |
| cobranca_id | Pagamento | Link | Pagamento |  |  |

### Audiencia

**Meta:** autoname=format:AUD-{####}, naming_rule=Expression (old style), title_field=tipo

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
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

**Meta:** autoname=format:CLI-{####}, naming_rule=Expression, title_field=nome

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

### Comarca

**Meta:** autoname=field:comarca_name, title_field=comarca_name

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| comarca_name | Nome da Comarca | Data |  | ✓ | ✓ |
| uf | UF | Select | AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO | ✓ |  |
| city | Cidade | Data |  |  |  |

### Comunicacao

**Meta:** autoname=format:COM-{YYYY}-{####}, naming_rule=Expression, title_field=assunto

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico |  |  |
| cliente | Cliente | Link | Cliente | ✓ |  |
| data | Data | Datetime |  | ✓ |  |
| tipo | Tipo | Select | Telefone WhatsApp Email Reunião Presencial Reunião Virtual Outro | ✓ |  |
| assunto | Assunto | Data |  | ✓ |  |
| resumo | Resumo | Text Editor |  |  |  |
| proximos_passos | Próximos Passos | Small Text |  |  |  |
| gerar_tarefa | Gerar Tarefa | Check |  |  |  |
| tarefa | Tarefa Gerada | Link | Tarefa |  |  |

### Configuracao do Escritorio

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| razao_social | Razão Social | Data |  | ✓ |  |
| cnpj | CNPJ | Data |  |  |  |
| registro_sia | Registro SIA | Data |  |  |  |
| advogada | Advogada(o) Principal | Data |  | ✓ |  |
| oab | OAB | Data |  | ✓ |  |
| endereco | Endereço Completo | Small Text |  | ✓ |  |

### Contato Cliente

**Meta:** istable

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| nome | Nome | Data |  | ✓ |  |
| tipo | Tipo | Select | Principal Conjuge Responsável Outro |  |  |
| telefone | Telefone | Data |  |  |  |
| celular | Celular | Data |  |  |  |
| email | E-mail | Data | Email |  |  |
| observacao | Observação | Small Text |  |  |  |

### Controle de Prazos

**Meta:** autoname=format:PRAZO-{####}, naming_rule=Expression (old style), title_field=descricao

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
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

**Meta:** autoname=format:CUST-{YYYY}-{####}, title_field=descricao

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| tipo | Tipo | Select | Taxa Judicial Perícia Certidão Deslocamento Cópia/Impressão Correios Cartório Diligência Outros | ✓ |  |
| descricao | Descrição | Data |  | ✓ |  |
| status | Status | Select | Pendente Pago Repassado Cancelado |  |  |
| valor | Valor | Currency |  | ✓ |  |
| data_pagamento | Data de Pagamento | Date |  |  |  |
| repassar_cliente | Repassar ao Cliente | Check |  |  |  |
| data_repasse | Data de Repasse | Date |  |  |  |
| forma_pagamento | Forma de Pagamento | Select | PIX TED Boleto Dinheiro Cartão |  |  |
| comprovante | Comprovante | Attach |  |  |  |
| observacoes | Observações | Small Text |  |  |  |

### Despesa do Escritorio

**Meta:** autoname=format:DESP-{YYYY}-{####}, title_field=descricao

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| descricao | Descrição | Data |  | ✓ |  |
| categoria | Categoria | Select | Aluguel Energia Água Internet Telefone Software/Assinatura Material de Escritório Impostos Contab... | ✓ |  |
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

### Endereco Cliente

**Meta:** istable

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tipo | Tipo | Select | Residencial Comercial Correspondência Outro |  |  |
| cep | CEP | Data |  |  |  |
| logradouro | Logradouro | Data |  | ✓ |  |
| numero | Número | Data |  |  |  |
| complemento | Complemento | Data |  |  |  |
| bairro | Bairro | Data |  |  |  |
| cidade | Cidade | Data |  |  |  |
| estado | Estado | Select |  AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO |  |  |
| principal | Endereço Principal | Check |  |  |  |

### Fase Processual

**Meta:** autoname=field:phase_name, title_field=phase_name

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| phase_name | Nome da Fase | Data |  | ✓ | ✓ |
| sort_order | Ordem | Int |  |  |  |

### Kit de Documentos

**Meta:** autoname=field:titulo, naming_rule=By fieldname, title_field=titulo

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Título | Data |  | ✓ | ✓ |
| descricao | Descrição | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| templates | Templates | Table | Kit Documento Item | ✓ |  |

### Kit Documento Item

**Meta:** istable

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| template | Template | Link | Template Documento | ✓ |  |
| ordem | Ordem | Int |  |  |  |

### Pagamento

**Meta:** autoname=naming_series:, naming_rule=By "Naming Series" field, title_field=descricao

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| naming_series | Série | Select | PAY-.YYYY.- |  |  |
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

### Parcela de Honorarios

**Meta:** istable

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| vencimento | Vencimento | Date |  | ✓ |  |
| valor_total | Valor Total | Currency |  |  |  |
| valor_advogada | Valor Advogada | Currency |  |  |  |
| valor_sucumbência | Valor Sucumbência | Currency |  |  |  |
| valor_cliente | Valor Cliente | Currency |  |  |  |
| descrição | Descrição | Small Text |  |  |  |
| parcela_origem_id | ID de Origem | Data |  |  |  |
| pagamento | Pagamento | Link | Pagamento |  |  |
| status | Status | Select | Pendente Vencido Recebido Repassado Cancelado |  |  |
| data_recebimento | Data de Recebimento | Date |  |  |  |
| data_repasse | Data de Repasse ao Cliente | Date |  |  |  |
| forma_recebimento | Forma de Recebimento | Select |  PIX TED Dinheiro Cartão Boleto |  |  |
| observacao | Observação | Small Text |  |  |  |

### Registro de Atos

**Meta:** autoname=format:ATOS-{####}, naming_rule=Expression (old style), title_field=title

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| status | Status | Select | Em aberto Parcialmente cobrado Cobrado |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| atos |  | Table | Ato Advocaticio |  |  |
| total_pendente | Total Pendente | Currency |  |  |  |
| total_cobrado | Total Cobrado | Currency |  |  |  |
| total_geral | Total Geral | Currency |  |  |  |
| data_vencimento_cobranca | Vencimento da Cobrança | Date |  |  |  |
| ultimo_pagamento | Último Pagamento | Link | Pagamento |  |  |
| gerar_cobranca | Sincronizar Cobrança | Button |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |
| title | Título | Data |  |  |  |

### Registro de Horas

**Meta:** autoname=format:HRS-{YYYY}-{####}, title_field=atividade

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico | ✓ |  |
| cliente | Cliente | Link | Cliente |  |  |
| data | Data | Date |  | ✓ |  |
| responsavel | Responsável | Link | User |  |  |
| hora_inicio | Hora Início | Time |  |  |  |
| hora_fim | Hora Fim | Time |  |  |  |
| duracao_minutos | Duração (min) | Int |  | ✓ |  |
| duracao_horas | Duração (horas) | Float |  |  |  |
| atividade | Atividade | Data |  | ✓ |  |
| categoria | Categoria | Select | Estudo/Pesquisa Redação Audiência Reunião Deslocamento Atendimento Administrativo Outro |  |  |
| descricao | Detalhes | Small Text |  |  |  |
| cobravel | Cobrável | Check |  |  |  |
| timer_display | Tempo Decorrido | HTML |  |  |  |
| timer_inicio | Início do Timer | Datetime |  |  |  |
| timer_ativo | Timer Ativo | Check |  |  |  |

### Servico

**Meta:** autoname=format:SERV-{####}, naming_rule=Expression (old style), title_field=title

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| cliente | Cliente | Link | Cliente | ✓ |  |
| tipo | Tipo | Select | Processo Judicial Consultoria Contrato Diligência Administrativo | ✓ |  |
| title | Título | Data |  |  |  |
| status | Status | Select | Em andamento Encerrado Suspenso Arquivado |  |  |
| fase_processual | Fase Processual | Link | Fase Processual |  |  |
| data_abertura | Data de Abertura | Date |  |  |  |
| numero_processo | Número do Processo | Data |  |  |  |
| numeracao_legada | Numeração legada (pré-CNJ) | Check |  |  |  |
| area | Área | Select |  Família Trabalhista Cível Criminal Previdenciário Administrativo Tributário |  |  |
| vara | Vara | Link | Vara |  |  |
| tribunal | Tribunal | Link | Tribunal |  |  |
| comarca | Comarca | Link | Comarca |  |  |
| parte_contraria | Parte Contrária | Data |  |  |  |
| valor_causa | Valor da Causa | Currency |  |  |  |
| observacoes | Observações | Text Editor |  |  |  |

### Tarefa

**Meta:** autoname=naming_series:, naming_rule=By "Naming Series" field, title_field=titulo

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| servico | Serviço | Link | Servico |  |  |
| cliente | Cliente | Link | Cliente |  |  |
| titulo | Título | Data |  | ✓ |  |
| status | Status | Select | Pendente Em Andamento Concluída Cancelada |  |  |
| prioridade | Prioridade | Select | Normal Alta Urgente |  |  |
| data_limite | Data Limite | Date |  |  |  |
| descricao | Descrição | Text Editor |  |  |  |
| responsavel | Responsável | Link | User |  |  |
| data_conclusao | Data de Conclusão | Date |  |  |  |
| naming_series | Série | Select | TAR-.YYYY.- |  |  |

### Template Documento

**Meta:** autoname=field:titulo, naming_rule=By fieldname, title_field=titulo

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| titulo | Titulo | Data |  | ✓ | ✓ |
| tipo_documento | Tipo de Documento | Select | Contrato Declaracao Recibo Carta Ficha de Atendimento Outro | ✓ |  |
| descricao | Descricao | Small Text |  |  |  |
| habilitado | Habilitado | Check |  |  |  |
| arquivo | Arquivo Template (.docx) | Attach |  | ✓ |  |
| ver_placeholders | Ver Placeholders Disponíveis | Button |  |  |  |

### Tribunal

**Meta:** autoname=field:tribunal_name, title_field=tribunal_name

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| tribunal_name | Nome do Tribunal | Data |  | ✓ | ✓ |
| abbreviation | Sigla | Data |  | ✓ | ✓ |
| jurisdiction | Esfera | Select | Estadual Federal Trabalho Superior Militar Eleitoral | ✓ |  |

### Vara

**Meta:** autoname=field:vara_name, title_field=vara_name

| fieldname | label | fieldtype | options | reqd | unique |
| --- | --- | --- | --- | --- | --- |
| vara_name | Nome da Vara | Data |  | ✓ | ✓ |
| comarca | Comarca | Link | Comarca | ✓ |  |
| court_type | Tipo | Select | Cível Criminal Família Trabalho Federal Juizado Especial Fazenda Pública |  |  |

### Grafo de links (resumo)

Cliente←Servico,Pagamento,... | Comarca←Vara,Servico | Pagamento←Parcela,Atos | Tarefa←Comunicacao

---

## 4. hooks.py

### fixtures
Workspace Advocacia; Notifications prazo/audiência; Custom Field Event custom_source%

### app_include_js (5)
- `/assets/advocacia/js/masks.js`
- `/assets/advocacia/js/list_nav.js`
- `/assets/advocacia/js/servico_link.js`
- `/assets/advocacia/js/cliente_from_servico.js`
- `/assets/advocacia/js/timer_global.js`

**Removido:** navegacao.js

### doc_events

| DocType | Evento | Handler |
| --- | --- | --- |
| Acordo de Honorarios Processuais | on_update | financeiro.sincronizar_pagamentos_hook |
| Parcela de Honorarios | on_update | tasks.on_parcela_update |
| Pagamento | on_update | financeiro.processar_pagamento_on_update |
| Pagamento | on_trash | financeiro.on_pagamento_trash |
| Audiencia | after_insert/on_update | calendar_sync.sync_audiencia_to_event |
| Controle de Prazos | after_insert/on_update | calendar_sync.sync_prazo_to_event |

### scheduler_events
- **daily:** verificar_parcelas_vencidas, verificar_despesas_vencidas, notificar_parcelas_vencidas, notificar_audiencias_hoje, notificar_prazos_diario
- **weekly:** verificar_status_servicos

### after_migrate
reinstalar_istable → after_install → event fields → translations → sidebar → reports → workspace

---

## 5. API whitelisted

| Função | Módulo | Permissão | Chamador |
| --- | --- | --- | --- |
| get_painel_data | painel_api→painel.get | has_permission Servico read | painel.js xcall |
| marcar_parcela_recebida | painel.financeiro | Pagamento write | painel.js |
| servico_query | servico | query padrão | Link Servico |
| get_link_title | servico | override desk | Frappe |
| gerar_documento_servico / em_lote | documentos | read/write Servico | servico.js |
| get_kits_disponiveis | documentos | read | servico.js |
| get_placeholders_referencia | documentos | read Template | template_documento.js |
| registrar_recebimento/repasse | parcela | check_permission write | form |
| concluir | tarefa | check_permission write | tarefa.js |
| timer APIs | registro_de_horas | check_permission | timer_global.js |
| get_events | audiencia/prazos | calendar read | calendar.js |
| gerar_proxima_despesa | despesa | create | form |
| financeiro sync/marcar | financeiro | has_permission | hooks/forms |

---

## 6. Schedulers

Ver seção 4 (tasks.py + notificacoes.py).

---

## 7. Client JS

5 globais; DocTypes: acordo (parcelas_add/remove), servico (bulk docx), audiencia (Híbrida), painel.js (~1800 linhas), calendars.

---

## 8. Setup / migrations

after_install + after_migrate idempotente; patches v16_0; commit só em setup/patches.

---

## 9. Reports (6)

- carteira_ativa
- fluxo_de_caixa
- honorarios_por_cliente
- inadimplencia
- horas_por_servico
- produtividade

---

## 10. Fixtures / Workspace / Sidebar

26 links cada; única divergência de label: fluxo_de_caixa (Fluxo de Caixa vs Fluxo de Caixa Projetado).

---

## 11. Testes

195 testes. `bench --site advocacia.local run-tests --app advocacia`

---

## 12. Integrações

calendar_sync → Event; documentos → docxtpl.

---

## 13. Backlog consciente

1. Chart.js ResizeObserver 2. fieldnames EN auxiliares 3. sql→qb painel 4. modularizar painel.js frontend
