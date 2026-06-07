# Manual do Usuário — Advocacia

**Gerado em:** 2026-06-06
**Versão do app:** 0.6.0

---

## Visão Geral

O sistema **Advocacia** centraliza clientes, processos, audiências, prazos, honorários, pagamentos e documentos para escritórios de advocacia brasileiros.

O **Serviço** funciona como hub: audiências, prazos, pagamentos e atos orbitam um serviço.

### Painel

Acesse `/app/painel` para KPIs, listas rápidas (prazos, audiências, tarefas) e atalhos de criação.

---

## Cadastros Básicos

### Cliente

Cadastro completo do cliente do escritório. Centraliza dados pessoais, documentação, endereços e contatos. Todo serviço jurídico está vinculado a um cliente.

**Código automático:** `format:CLI-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Tipo de Pessoa | Select | ✅ | Pessoa Física ou Pessoa Jurídica. Define quais documentos são obrigatórios. |
| Nome / Razão Social | Data | ✅ | Nome completo (PF) ou razão social (PJ). Aparece como título do registro. |
| Nome Fantasia | Data |  | Nome fantasia da empresa (apenas pessoa jurídica). |
| CPF | Data |  | CPF do cliente. Apenas dígitos, validado automaticamente. |
| RG | Data |  | Documento de identidade (pessoa física). |
| CNPJ | Data |  | CNPJ do cliente. Apenas dígitos, validado automaticamente. |
| Nacionalidade | Data |  | Nacionalidade do cliente (pessoa física). |
| Estado Civil | Select |  | Estado civil (pessoa física). |
| Profissão | Data |  | Profissão declarada (pessoa física). |
| Representante Legal | Data |  | Nome do representante legal (pessoa jurídica). |
| CPF do Representante | Data |  | CPF do representante legal, com validação automática. |
| Cargo | Data |  | Cargo do representante legal na empresa. |
| Nacionalidade do Representante | Data |  | Nacionalidade do representante legal. |
| Contatos | Table |  | Telefones e e-mails de contato do cliente. |
| Endereços | Table |  | Endereços do cliente. Marque um como principal para documentos. |
| Observações | Text Editor |  | Anotações internas sobre o cliente. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Comarca

Divisão judiciária geográfica. Cadastro rígido para consistência.

**Código automático:** `field:comarca_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Comarca | Data | ✅ | Nome único da comarca. Usado como identificador do registro. |
| UF | Select | ✅ | Unidade federativa (UF) da comarca. |
| Cidade | Data |  | Cidade sede da comarca. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Vara

Unidade judicial dentro de uma comarca.

**Código automático:** `field:vara_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Vara | Data | ✅ | Nome único da vara. Usado como identificador do registro. |
| Comarca | Link | ✅ | Comarca à qual esta vara pertence. |
| Tipo | Select |  | Tipo: Cível, Criminal, Família, Trabalho, Federal ou Juizado Especial. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Tribunal

Tribunal de justiça competente (ex.: TJRS, TRF4).

**Código automático:** `field:tribunal_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome do Tribunal | Data | ✅ | Nome único do tribunal. |
| Sigla | Data | ✅ | Sigla oficial (ex.: TJRS, TRT4). |
| Esfera | Select | ✅ | Esfera: Estadual, Federal, Trabalho, Superior ou Militar. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Fase Processual

Fase do processo no fluxo (Distribuído, Sentenciado, etc.).

**Código automático:** `field:phase_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Fase | Data | ✅ | Nome da fase (ex.: Conhecimento, Execução). |
| Ordem | Int |  | Ordem de exibição no fluxo processual. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Serviço Jurídico (Hub Central)

### Servico

O **Serviço** é o DocType central (hub) do sistema. Representa um processo judicial ou consultoria jurídica. Audiências, prazos, pagamentos e atos orbitam um Serviço.

**Código automático:** `format:SERV-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Cliente | Link | ✅ | Cliente titular deste serviço ou processo. |
| Tipo | Select | ✅ | Consultoria ou Processo Judicial. Define campos e validações do formulário. |
| Título | Data |  | Título automático no formato ID — cliente. Atualizado ao salvar. |
| Status | Select |  | Em andamento, Arquivado, Suspenso ou Encerrado. |
| Fase Processual | Link |  | Fase atual do processo conforme cadastro rígido de Fases Processuais. |
| Data de Abertura | Date |  | Data de abertura do serviço ou distribuição do processo. |
| Número do Processo | Data |  | Número CNJ do processo (validado automaticamente). Obrigatório para Processo Judicial. |
| Numeração legada (pré-CNJ) | Check |  | Número antigo ou interno, se diferente do CNJ. |
| Área | Select |  | Área do direito: Cível, Criminal, Trabalhista, etc. |
| Vara | Link |  | Vara judicial vinculada (cadastro rígido). |
| Tribunal | Link |  | Tribunal competente (cadastro rígido). |
| Comarca | Link |  | Comarca onde o processo tramita (cadastro rígido). |
| Parte Contrária | Data |  | Nome da parte adversa, quando aplicável. |
| Valor da Causa | Currency |  | Valor atribuído à causa na petição inicial. |
| Observações | Text Editor |  | Anotações internas sobre o serviço ou processo. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Financeiro

### Acordo de Honorarios Processuais

Define honorários contratados com o cliente, parcelas e vencimentos. O sistema sincroniza parcelas com registros de Pagamento.

**Código automático:** `format:ACOR-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado ao acordo. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Modo | Select | ✅ | Honorários Diretos ou Repasse de Sucumbência. |
| Status | Select |  | Vigente, Quitado ou Cancelado. |
| Valor Total do Acordo | Currency |  | Valor total acordado entre as partes. |
| Percentual Advogada (%) | Percent |  | Percentual da advogada sobre o total (modo repasse). |
| Valor Fixo de Honorários | Currency |  | Valor fixo de honorários (modo misto). |
| Valor Advogada | Currency |  | Parcela destinada à advogada. |
| Tipo de cobrança | Select | ✅ | Forma de cálculo: valor fixo, percentual ou misto. |
| Percentual Cliente | Percent |  | Percentual do cliente sobre o total. |
| Valor Cliente | Currency |  | Parcela destinada ao cliente (repasse). |
| Tipo de cálculo | Select |  | Forma de cálculo da sucumbência: percentual ou valor fixo. |
| Percentual Sucumbência (%) | Percent |  | Percentual sobre a sucumbência. |
| Honorários de Sucumbência | Currency |  | Valor de honorários de sucumbência. |
| Status da Sucumbência | Select |  | Situação da sucumbência: pendente, recebida, etc. |
| Número de Parcelas | Int |  | Quantidade de parcelas planejadas. |
| Data Primeira Parcela | Date |  | Vencimento da primeira parcela. |
| Valor da Parcela | Currency |  | Valor médio por parcela (referência). |
|  | Table |  | Parcelas do acordo. Ao salvar, o sistema gera ou atualiza os pagamentos. |
| Total Advogada | Currency |  | Soma das parcelas da advogada. Calculado automaticamente. |
| Total Cliente | Currency |  | Soma das parcelas do cliente. Calculado automaticamente. |
| Observações | Text Editor |  | Observações contratuais e anotações internas. |
| Título | Data |  | Título automático no formato ID — cliente. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Pagamento

Registro operacional de recebimento. Diferente da Parcela (contratual), registra o dinheiro que efetivamente entrou no escritório.

**Código automático:** `format:PAG-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Origem | Select |  | Honorários (Parcela) ou Atos Advocatícios. |
| Acordo | Link |  | Acordo de honorários que originou este pagamento (parcelas). |
| Registro de Atos | Link |  | Registro de atos vinculado (cobrança de atos). |
| Serviço | Link | ✅ | Serviço ou processo relacionado. |
| Cliente | Link | ✅ | Preenchido automaticamente a partir do serviço ou acordo. |
| Nº Parcela | Int |  | Número sequencial da parcela no acordo. |
| Descrição | Small Text |  | Descrição exibida na parcela e nos relatórios. |
| ID Origem | Data |  | Identificador interno para sincronização com parcelas do acordo. |
| Sincronizado em | Datetime |  | Data e hora da última sincronização automática. |
| Edição manual (não sincronizar) | Check |  | Quando marcado, o sistema não sobrescreve este pagamento na sincronização. |
| Valor | Currency | ✅ | Valor previsto da parcela ou cobrança. |
| Valor Recebido | Currency |  | Valor efetivamente recebido. |
| Vencimento | Date | ✅ | Data de vencimento. |
| Data de Recebimento | Date |  | Data em que o pagamento foi recebido. |
| Status | Select | ✅ | Pendente, Vencido, Recebido, Repassado, Cancelado ou Renegociado. |
| Observações | Small Text |  | Observações internas sobre o pagamento. |
| Comprovante | Attach |  | Comprovante de recebimento anexado. |
| Título | Data |  | Título automático com ID e descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Custa Processual

**Código automático:** `format:CUST-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado à custa. |
| Cliente | Link |  | Selecione o registro vinculado. Preenchido ou calculado automaticamente pelo sistema. |
| Tipo | Select | ✅ | Taxa Judicial, Emolumento, Despesa Cartorial, etc. |
| Descrição | Data | ✅ | Descrição da custa ou taxa. |
| Status | Select |  | Pendente, Pago, Repassado ou Cancelado. |
| Valor | Currency | ✅ | Valor da custa em reais. |
| Data de Pagamento | Date |  | Data em que a custa foi paga. |
| Repassar ao Cliente | Check |  | Marque se o valor deve ser repassado ao cliente. |
| Data de Repasse | Date |  | Data do repasse ao cliente. |
| Forma de Pagamento | Select |  | Forma de pagamento: PIX, TED, Dinheiro, etc. |
| Comprovante | Attach |  | Comprovante de pagamento anexado. |
| Observações | Small Text |  | Observações sobre a custa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Despesa do Escritorio

**Código automático:** `format:DESP-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Descrição | Data | ✅ | Descrição da despesa (ex.: aluguel, internet). |
| Categoria | Select | ✅ | Categoria: Aluguel, Salários, Software, etc. |
| Valor | Currency | ✅ | Valor da despesa em reais. |
| Status | Select |  | Pendente, Pago ou Atrasado. |
| Data de Vencimento | Date |  | Data de vencimento. |
| Data de Pagamento | Date |  | Data em que a despesa foi paga. |
| Forma de Pagamento | Select |  | Forma de pagamento: PIX, TED, Boleto, etc. |
| Despesa Recorrente | Check |  | Marque se a despesa se repete periodicamente. |
| Frequência | Select |  | Frequência da recorrência: Mensal, Anual, etc. |
| Próximo Vencimento | Date |  | Próximo vencimento calculado (despesas recorrentes). |
| Comprovante | Attach |  | Comprovante de pagamento anexado. |
| Observações | Small Text |  | Observações sobre a despesa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Acompanhamento Processual

### Audiencia

Audiências judiciais vinculadas a um serviço. Sincroniza com o calendário Frappe (Google Calendar).

**Código automático:** `format:AUD-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado à audiência. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Data e Hora | Datetime | ✅ | Data e hora da audiência. |
| Status | Select |  | Agendada, Realizada, Adiada ou Cancelada. |
| Tipo | Select | ✅ | Tipo de audiência: Conciliação, Instrução, etc. |
| Modalidade | Select |  | Presencial, Virtual ou Híbrida. |
| Link da Audiência Virtual | Data |  | Link de acesso para audiência virtual ou híbrida. |
| Vara | Link |  | Vara ou local da audiência (cadastro rígido). |
| Resultado | Select |  | Resultado ou desfecho da audiência. |
| Observações | Text Editor |  | Anotações sobre a audiência. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Controle de Prazos

Prazos processuais com data fatal. Notificações automáticas para prazos urgentes (≤3 dias).

**Código automático:** `format:PRAZO-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado ao prazo. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Data do Prazo | Date | ✅ | Data fatal do prazo processual. |
| Status | Select |  | Pendente, Concluído ou Vencido. Vencido é atualizado automaticamente. |
| Descrição | Small Text | ✅ | Descrição do compromisso ou prazo (ex.: contestação, recurso). |
| Prioridade | Select |  | Baixa, Média, Alta ou Urgente — usada em alertas e no painel. |
| Responsável | Link |  | Usuário responsável pelo cumprimento do prazo. |
| Notificar com antecedência (dias) | Int |  | Quantos dias antes do vencimento enviar alerta. |
| Observações | Text Editor |  | Observações adicionais sobre o prazo. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Tarefa

**Código automático:** `format:TAR-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link |  | Serviço relacionado (opcional). |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Descrição da Tarefa | Data | ✅ | Descrição curta da tarefa. |
| Status | Select |  | Pendente, Em Andamento, Concluída ou Cancelada. |
| Prioridade | Select |  | Baixa, Média ou Alta. |
| Data Limite | Date |  | Prazo para conclusão da tarefa (opcional). |
| Descrição | Text Editor |  | Detalhamento da tarefa e instruções. |
| Responsável | Link |  | Usuário responsável pela execução. |
| Data de Conclusão | Date |  | Preenchida automaticamente ao concluir a tarefa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Comunicacao

**Código automático:** `format:COM-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link |  | Serviço relacionado à comunicação (opcional). |
| Cliente | Link | ✅ | Cliente envolvido na comunicação. |
| Data | Datetime | ✅ | Data e hora da comunicação. |
| Tipo | Select | ✅ | Canal: Telefone, WhatsApp, E-mail, Reunião, etc. |
| Assunto | Data | ✅ | Assunto principal da comunicação. |
| Resumo | Text Editor |  | Resumo do que foi tratado. |
| Próximos Passos | Small Text |  | Próximos passos combinados (opcional). |
| Gerar Tarefa | Check |  | Marque para criar tarefa automaticamente a partir deste registro. |
| Tarefa Gerada | Link |  | Tarefa gerada a partir desta comunicação. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Registro de Atividades

### Registro de Atos

**Código automático:** `format:ATOS-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado aos atos. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Status | Select |  | Em aberto, Parcialmente cobrado ou Cobrado. |
| Data de Abertura | Date |  | Data de abertura do registro de atos. |
|  | Table |  | Atos advocatícios acumulados para cobrança. |
| Total Pendente | Currency |  | Soma dos atos pendentes. Calculado automaticamente. |
| Total Cobrado | Currency |  | Soma dos atos já cobrados. Calculado automaticamente. |
| Total Geral | Currency |  | Total geral dos atos. Calculado automaticamente. |
| Vencimento da Cobrança | Date |  | Vencimento sugerido ao gerar cobrança dos atos pendentes. |
| Último Pagamento | Link |  | Último pagamento de atos vinculado a este registro. |
| Observações | Text Editor |  | Observações sobre o registro de atos. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Registro de Horas

**Código automático:** `format:HRS-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço onde a atividade foi realizada. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Data | Date | ✅ | Data da atividade. |
| Responsável | Link |  | Profissional que registrou a atividade. |
| Hora Início | Time |  | Hora de início (timer). |
| Hora Fim | Time |  | Hora de término (timer). |
| Duração (min) | Int |  | Duração em minutos. Use o timer ou informe manualmente. |
| Duração (horas) | Float |  | Duração convertida em horas. Calculada automaticamente. |
| Atividade | Data | ✅ | Descrição curta da atividade realizada. |
| Categoria | Select |  | Categoria da atividade: Reunião, Petição, Pesquisa, etc. |
| Detalhes | Small Text |  | Detalhamento complementar da atividade. |
| Cobrável | Check |  | Marque se o tempo deve entrar em relatórios de cobrança. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Documentos

### Template Documento

Modelo .docx com placeholders para geração automática.

**Código automático:** `field:titulo`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Titulo | Data | ✅ | Nome do modelo. Identificador único no catálogo. |
| Tipo de Documento | Select | ✅ | Tipo: Petição, Contrato, Procuração, etc. |
| Descricao | Small Text |  | Descrição do uso deste modelo. |
| Habilitado | Check |  | Desmarque para ocultar o modelo na geração de documentos. |
| Arquivo Template (.docx) | Attach | ✅ | Arquivo .docx com placeholders para geração. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Kit de Documentos

Conjunto de templates para geração em lote.

**Código automático:** `field:titulo`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Título | Data | ✅ | Nome do kit. Identificador único. |
| Descrição | Small Text |  | Descrição do conjunto de modelos incluídos. |
| Habilitado | Check |  | Desmarque para desabilitar o kit na geração em lote. |
| Templates | Table | ✅ | Modelos de documento incluídos neste kit. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Configuração

### Configuracao do Escritorio

Dados institucionais do escritório (OAB, CNPJ, endereço).

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Razão Social | Data | ✅ | Razão social do escritório. Usada em documentos gerados. |
| CNPJ | Data |  | CNPJ do escritório. Usado em contratos e documentos oficiais. |
| Registro SIA | Data |  | Registro no SIA/OAB do escritório. |
| Advogada(o) Principal | Data | ✅ | Nome da advogada responsável pelo escritório. |
| OAB | Data | ✅ | Número da OAB (apenas dígitos). |
| Endereço Completo | Small Text | ✅ | Endereço completo do escritório para documentos. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Fluxos Comuns

### Novo Processo
1. Cadastre o **Cliente**
2. Crie um **Serviço** com vara, comarca e tribunal
3. Defina **Acordo de Honorários** com parcelas
4. Cadastre **Audiências** e **Prazos**

### Recebimento
1. Registre **Pagamento** quando o cliente pagar
2. O painel atualiza KPIs financeiros

---

*Regenerar: `bench execute advocacia.advocacia.scripts.generate_manual.generate`*