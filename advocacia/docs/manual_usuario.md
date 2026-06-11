# Manual do Usuário — Advocacia

**Gerado em:** 2026-06-11
**Versão do app:** 0.7.0

---

## Visão Geral

O sistema **Advocacia** centraliza clientes, processos, audiências, prazos, honorários, pagamentos e documentos para escritórios de advocacia brasileiros.

O **Serviço** funciona como hub: audiências, prazos, pagamentos e atos orbitam um serviço.

### Painel

Acesse `/app/painel` para KPIs, listas rápidas (prazos, audiências, tarefas) e atalhos de criação.

---

## Cadastros Básicos

### Client

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

### Jurisdiction

Divisão judiciária geográfica. Cadastro rígido para consistência.

**Código automático:** `field:jurisdiction_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Jurisdiction | Data | ✅ | Nome único da comarca. Usado como identificador do registro. |
| UF | Select | ✅ | Unidade federativa (UF) da comarca. |
| Cidade | Data |  | Cidade sede da comarca. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Court Branch

Unidade judicial dentro de uma comarca.

**Código automático:** `field:court_branch_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Court Branch | Data | ✅ | Nome único da vara. Usado como identificador do registro. |
| Jurisdiction | Link | ✅ | Jurisdiction à qual esta vara pertence. |
| Tipo | Select |  | Tipo: Cível, Criminal, Família, Trabalho, Federal ou Juizado Especial. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Court

Court de justiça competente (ex.: TJRS, TRF4).

**Código automático:** `field:court_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome do Court | Data | ✅ | Nome único do tribunal. |
| Sigla | Data | ✅ | Sigla oficial (ex.: TJRS, TRT4). |
| Esfera | Select | ✅ | Esfera: Estadual, Federal, Trabalho, Superior ou Militar. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Case Phase

Fase do processo no fluxo (Distribuído, Sentenciado, etc.).

**Código automático:** `field:case_phase_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Nome da Fase | Data | ✅ | Nome da fase (ex.: Conhecimento, Execução). |
| Ordem | Int |  | Ordem de exibição no fluxo processual. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Serviço Jurídico (Hub Central)

### Legal Case

O **Serviço** é o DocType central (hub) do sistema. Representa um processo judicial ou consultoria jurídica. Audiências, prazos, pagamentos e atos orbitam um Serviço.

**Código automático:** `format:SERV-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Client | Link | ✅ | Client titular deste serviço ou processo. |
| Tipo | Select | ✅ | Consultoria ou Processo Judicial. Define campos e validações do formulário. |
| Título | Data |  | Título automático no formato ID — cliente. Atualizado ao salvar. |
| Status | Select |  | Em andamento, Arquivado, Suspenso ou Encerrado. |
| Case Phase | Link |  | Fase atual do processo conforme cadastro rígido de Fases Processuais. |
| Data de Abertura | Date |  | Data de abertura do serviço ou distribuição do processo. |
| Número do Processo | Data |  | Número CNJ do processo (validado automaticamente). Obrigatório para Processo Judicial. |
| Numeração legada (pré-CNJ) | Check |  | Número antigo ou interno, se diferente do CNJ. |
| Área | Select |  | Área do direito: Cível, Criminal, Trabalhista, etc. |
| Court Branch | Link |  | Court Branch judicial vinculada (cadastro rígido). |
| Court | Link |  | Court competente (cadastro rígido). |
| Jurisdiction | Link |  | Jurisdiction onde o processo tramita (cadastro rígido). |
| Parte Contrária | Data |  | Nome da parte adversa, quando aplicável. |
| Valor da Causa | Currency |  | Valor atribuído à causa na petição inicial. |
| Observações | Text Editor |  | Anotações internas sobre o serviço ou processo. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Financeiro

### Fee Agreement

Define honorários contratados com o cliente, parcelas e vencimentos. O sistema sincroniza parcelas com registros de Legal Payment.

**Código automático:** `format:ACOR-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado ao acordo. |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
| Modo | Select | ✅ | Honorários Diretos ou Repasse de Sucumbência. |
| Status | Select |  | Vigente, Quitado ou Cancelado. |
| Valor Total do Acordo | Currency |  | Valor total acordado entre as partes. |
| Percentual Advogada (%) | Percent |  | Percentual da advogada sobre o total (modo repasse). |
| Valor Fixo de Honorários | Currency |  | Valor fixo de honorários (modo misto). |
| Valor Advogada | Currency |  | Parcela destinada à advogada. |
| Tipo de cobrança | Select | ✅ | Forma de cálculo: valor fixo, percentual ou misto. |
| Percentual Client | Percent |  | Percentual do cliente sobre o total. |
| Valor Client | Currency |  | Parcela destinada ao cliente (repasse). |
| Tipo de cálculo | Select |  | Forma de cálculo da sucumbência: percentual ou valor fixo. |
| Percentual Sucumbência (%) | Percent |  | Percentual sobre a sucumbência. |
| Honorários de Sucumbência | Currency |  | Valor de honorários de sucumbência. |
| Status da Sucumbência | Select |  | Situação da sucumbência: pendente, recebida, etc. |
| Número de Parcelas | Int |  | Quantidade de parcelas planejadas. |
| Data Primeira Parcela | Date |  | Vencimento da primeira parcela. |
| Valor da Parcela | Currency |  | Valor médio por parcela (referência). |
| Gerar Parcelas | Button |  |  |
|  | Table |  | Parcelas do acordo. Ao salvar, o sistema gera ou atualiza os pagamentos. |
| Total Advogada | Currency |  | Soma das parcelas da advogada. Calculado automaticamente. |
| Total Client | Currency |  | Soma das parcelas do cliente. Calculado automaticamente. |
| Observações | Text Editor |  | Observações contratuais e anotações internas. |
| Título | Data |  | Título automático no formato ID — cliente. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Legal Payment

Registro operacional de recebimento. Diferente da Parcela (contratual), registra o dinheiro que efetivamente entrou no escritório.

**Código automático:** `format:PAG-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Origem | Select |  | Honorários (Parcela) ou Atos Advocatícios. |
| Acordo | Link |  | Acordo de honorários que originou este pagamento (parcelas). |
| Service Record | Link |  | Registro de atos vinculado (cobrança de atos). |
| Serviço | Link | ✅ | Serviço ou processo relacionado. |
| Client | Link | ✅ | Preenchido automaticamente a partir do serviço ou acordo. |
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

### Court Cost

**Código automático:** `format:CUST-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado à custa. |
| Client | Link |  | Selecione o registro vinculado. Preenchido ou calculado automaticamente pelo sistema. |
| Tipo | Select | ✅ | Taxa Judicial, Emolumento, Despesa Cartorial, etc. |
| Descrição | Data | ✅ | Descrição da custa ou taxa. |
| Status | Select |  | Pendente, Pago, Repassado ou Cancelado. |
| Valor | Currency | ✅ | Valor da custa em reais. |
| Data de Legal Payment | Date |  | Data em que a custa foi paga. |
| Repassar ao Client | Check |  | Marque se o valor deve ser repassado ao cliente. |
| Data de Repasse | Date |  | Data do repasse ao cliente. |
| Forma de Legal Payment | Select |  | Forma de pagamento: PIX, TED, Dinheiro, etc. |
| Comprovante | Attach |  | Comprovante de pagamento anexado. |
| Observações | Small Text |  | Observações sobre a custa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Office Expense

**Código automático:** `format:DESP-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Descrição | Data | ✅ | Descrição da despesa (ex.: aluguel, internet). |
| Categoria | Select | ✅ | Categoria: Aluguel, Salários, Software, etc. |
| Valor | Currency | ✅ | Valor da despesa em reais. |
| Status | Select |  | Pendente, Pago ou Atrasado. |
| Data de Vencimento | Date |  | Data de vencimento. |
| Data de Legal Payment | Date |  | Data em que a despesa foi paga. |
| Forma de Legal Payment | Select |  | Forma de pagamento: PIX, TED, Boleto, etc. |
| Despesa Recorrente | Check |  | Marque se a despesa se repete periodicamente. |
| Frequência | Select |  | Frequência da recorrência: Mensal, Anual, etc. |
| Próximo Vencimento | Date |  | Próximo vencimento calculado (despesas recorrentes). |
| Comprovante | Attach |  | Comprovante de pagamento anexado. |
| Observações | Small Text |  | Observações sobre a despesa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Acompanhamento Processual

### Hearing

Audiências judiciais vinculadas a um serviço. Sincroniza com o calendário Frappe (Google Calendar).

**Código automático:** `format:AUD-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado à audiência. |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
| Data e Hora | Datetime | ✅ | Data e hora da audiência. |
| Status | Select |  | Agendada, Realizada, Adiada ou Cancelada. |
| Tipo | Select | ✅ | Tipo de audiência: Conciliação, Instrução, etc. |
| Modalidade | Select |  | Presencial, Virtual ou Híbrida. |
| Link da Audiência Virtual | Data |  | Link de acesso para audiência virtual ou híbrida. |
| Court Branch | Link |  | Court Branch ou local da audiência (cadastro rígido). |
| Resultado | Select |  | Resultado ou desfecho da audiência. |
| Observações | Text Editor |  | Anotações sobre a audiência. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Deadline

Prazos processuais com data fatal. Notificações automáticas usam `notification_days` do prazo ou o padrão de Office Settings.

**Código automático:** `format:PRAZO-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado ao prazo. |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
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

### Legal Task

**Código automático:** `format:TAR-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link |  | Serviço relacionado (opcional). |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
| Descrição da Legal Task | Data | ✅ | Descrição curta da tarefa. |
| Status | Select |  | Pendente, Em Andamento, Concluída ou Cancelada. |
| Prioridade | Select |  | Baixa, Média ou Alta. |
| Data Limite | Date |  | Prazo para conclusão da tarefa (opcional). |
| Descrição | Text Editor |  | Detalhamento da tarefa e instruções. |
| Responsável | Link |  | Usuário responsável pela execução. |
| Data de Conclusão | Date |  | Preenchida automaticamente ao concluir a tarefa. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Case Communication

**Código automático:** `format:COM-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link |  | Serviço relacionado à comunicação (opcional). |
| Client | Link | ✅ | Client envolvido na comunicação. |
| Data | Datetime | ✅ | Data e hora da comunicação. |
| Tipo | Select | ✅ | Canal: Telefone, WhatsApp, E-mail, Reunião, etc. |
| Assunto | Data | ✅ | Assunto principal da comunicação. |
| Resumo | Text Editor |  | Resumo do que foi tratado. |
| Próximos Passos | Small Text |  | Próximos passos combinados (opcional). |
| Gerar Legal Task | Check |  | Marque para criar tarefa automaticamente a partir deste registro. |
| Legal Task Gerada | Link |  | Legal Task gerada a partir desta comunicação. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Registro de Atividades

### Service Record

**Código automático:** `format:ATOS-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço ou processo vinculado aos atos. |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
| Status | Select |  | Em aberto, Parcialmente cobrado ou Cobrado. |
| Data de Abertura | Date |  | Data de abertura do registro de atos. |
|  | Table |  | Atos advocatícios acumulados para cobrança. |
| Total Pendente | Currency |  | Soma dos atos pendentes. Calculado automaticamente. |
| Total Cobrado | Currency |  | Soma dos atos já cobrados. Calculado automaticamente. |
| Total Geral | Currency |  | Total geral dos atos. Calculado automaticamente. |
| Vencimento da Cobrança | Date |  | Vencimento sugerido ao gerar cobrança dos atos pendentes. |
| Último Legal Payment | Link |  | Último pagamento de atos vinculado a este registro. |
| Sincronizar Cobrança | Button |  |  |
| Observações | Text Editor |  | Observações sobre o registro de atos. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Time Entry

**Código automático:** `format:HRS-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço onde a atividade foi realizada. |
| Client | Link |  | Preenchido automaticamente a partir do serviço. |
| Data | Date | ✅ | Data da atividade. |
| Responsável | Link |  | Profissional que registrou a atividade. |
| Hora Início | Time |  | Hora de início (timer). |
| Hora Fim | Time |  | Hora de término (timer). |
| Duração (min) | Int |  | Duração em minutos. Use o timer ou informe manualmente. |
| Duração (horas) | Float |  | Duração convertida em horas. Calculada automaticamente. |
| Atividade | Data | ✅ | Descrição curta da atividade realizada. |
| Categoria | Select |  | Categoria da atividade: Reunião, Petição, Pesquisa, etc. |
| Cobrável | Check |  | Marque se o tempo deve entrar em relatórios de cobrança. |
| Detalhes | Small Text |  | Detalhamento complementar da atividade. |
| Título | Data |  | Título automático no formato ID — descritor. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Documentos

### Document Category

Categoria documental rígida (Petição, Procuração, Contrato, etc.). Usada para organizar **Case Document** e relatórios.

**Código automático:** `field:category_name`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Categoria | Data | ✅ | Nome único da categoria documental (ex.: Petição, Procuração, Laudo). |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Case Document

Arquivo do processo vinculado a um **Serviço**. Pode ser enviado manualmente ou criado automaticamente ao gerar documentos Word.

**Código automático:** `format:DOC-{YYYY}-{####}`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Serviço | Link | ✅ | Serviço (processo ou consultoria) ao qual este documento pertence. |
| Cliente | Link |  | Preenchido automaticamente a partir do serviço. |
| Categoria | Link | ✅ | Tipo documental para organização e relatórios. |
| Status | Select | ✅ | Situação do documento no fluxo do processo. |
| Origem | Select |  | Como o arquivo entrou no sistema. |
| Título | Data |  | Composto automaticamente: {Categoria} — {Serviço}[ — {Versão}]. |
| Versão / Revisão | Data |  | Ex.: Rev 01, v2 assinada. |
| Arquivo | Attach | ✅ | Arquivo anexado (PDF, DOCX, imagem, etc.). |
| Prazo Relacionado | Link |  | Prazo vinculado a este documento (opcional). |
| Observações | Small Text |  | Notas internas sobre o documento. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Document Template

Modelo .docx com placeholders para geração automática. Use o botão **Ver Placeholders Disponíveis** para a lista completa.

**Código automático:** `field:title`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Titulo | Data | ✅ | Nome do modelo. Identificador único no catálogo. |
| Tipo de Documento | Select | ✅ | Tipo: Petição, Contrato, Procuração, etc. |
| Descricao | Small Text |  | Descrição do uso deste modelo. |
| Habilitado | Check |  | Desmarque para ocultar o modelo na geração de documentos. |
| Arquivo Template (.docx) | Attach | ✅ | Arquivo .docx com placeholders para geração. |
| Ver Placeholders Disponíveis | Button |  | Abre a referência de placeholders disponíveis no modelo. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Document Kit

Conjunto de templates para geração em lote.

**Código automático:** `field:title`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Título | Data | ✅ | Nome do kit. Identificador único. |
| Descrição | Small Text |  | Descrição do conjunto de modelos incluídos. |
| Habilitado | Check |  | Desmarque para desabilitar o kit na geração em lote. |
| Templates | Table | ✅ | Modelos de documento incluídos neste kit. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

### Placeholders para templates .docx

Sintaxe **docxtpl**: `{{ nome_do_campo }}`. Grupos *condicionais* só têm valor quando há acordo de honorários vinculado. A logo usa `{{ escritorio_logo }}` como imagem inline.

#### Escritório

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ escritorio_razao_social }}` | Razão social do escritório | — |
| `{{ escritorio_cnpj }}` | CNPJ do escritório (mascarado) | — |
| `{{ escritorio_oab }}` | OAB do escritório | — |
| `{{ escritorio_advogada }}` | Advogada(o) principal | — |
| `{{ escritorio_endereco }}` | Endereço profissional | — |
| `{{ escritorio_registro }}` | Registro SIA/OAB | — |
| `{{ escritorio_logo }}` | Logo do escritório (imagem — somente em .docx) | — |
| `{{ escritorio_banco }}` | Banco | — |
| `{{ escritorio_agencia }}` | Agência | — |
| `{{ escritorio_conta }}` | Conta corrente | — |
| `{{ escritorio_pix }}` | Chave PIX | — |

#### Cliente

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ cliente_nome }}` | Nome / razão social | `{{ nome }}` |
| `{{ cliente_tipo_pessoa }}` | Tipo de pessoa (PF/PJ) | — |
| `{{ cliente_cpf }}` | CPF (mascarado) | `{{ cpf }}` |
| `{{ cliente_cnpj }}` | CNPJ (mascarado) | `{{ cnpj }}` |
| `{{ cliente_rg }}` | RG | `{{ rg }}` |
| `{{ cliente_nacionalidade }}` | Nacionalidade | `{{ nacionalidade }}` |
| `{{ cliente_estado_civil }}` | Estado civil | `{{ estado_civil }}` |
| `{{ cliente_profissao }}` | Profissão | `{{ profissao }}` |
| `{{ cliente_representante }}` | Representante legal | `{{ representante }}` |
| `{{ cliente_cpf_representante }}` | CPF do representante | `{{ cpf_representante }}` |
| `{{ cliente_cargo_representante }}` | Cargo do representante | — |
| `{{ cliente_nome_fantasia }}` | Nome fantasia | — |

#### Endereço do cliente

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ endereco_logradouro }}` | Logradouro | `{{ endereco }}` |
| `{{ endereco_numero }}` | Número | `{{ numero }}` |
| `{{ endereco_complemento }}` | Complemento | `{{ complemento }}` |
| `{{ endereco_bairro }}` | Bairro | `{{ bairro }}` |
| `{{ endereco_cidade }}` | Cidade | `{{ cidade }}` |
| `{{ endereco_estado }}` | UF | `{{ estado }}` |
| `{{ endereco_cep }}` | CEP (mascarado) | `{{ cep }}` |
| `{{ endereco_completo }}` | Endereço completo formatado | — |

#### Contato

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ contato_nome }}` | Nome do contato | — |
| `{{ contato_telefone }}` | Telefone fixo | `{{ telefone }}` |
| `{{ contato_celular }}` | Celular | — |
| `{{ contato_email }}` | E-mail | `{{ email }}` |
| `{{ telefone_contato }}` | Telefone principal (legado) | — |

#### Serviço / processo

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ servico_codigo }}` | Código do serviço (ID) | `{{ legal_case }}` |
| `{{ servico_titulo }}` | Título do serviço | `{{ titulo_servico }}` |
| `{{ servico_tipo }}` | Tipo de serviço | `{{ tipo_servico }}` |
| `{{ servico_status }}` | Status do serviço | — |
| `{{ servico_numero_processo }}` | Número do processo (CNJ) | `{{ numero_processo }}` |
| `{{ servico_area }}` | Área jurídica | `{{ area }}` |
| `{{ servico_vara }}` | Vara | `{{ court_branch_link }}` |
| `{{ servico_comarca }}` | Comarca | `{{ jurisdiction }}` |
| `{{ servico_tribunal }}` | Tribunal | — |
| `{{ servico_fase_processual }}` | Fase processual | — |
| `{{ servico_parte_contraria }}` | Parte contrária | `{{ parte_contraria }}` |
| `{{ servico_valor_causa }}` | Valor da causa (R$) | `{{ valor_causa }}` |
| `{{ servico_data_abertura }}` | Data de abertura | `{{ data_abertura }}` |

#### Acordo de honorários *(condicional)*

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ acordo_modo_honorarios }}` | Modo de honorários | — |
| `{{ acordo_status }}` | Status do acordo | — |
| `{{ acordo_valor_total_do_acordo }}` | Valor total do acordo (R$) | — |
| `{{ acordo_percentual_advogada }}` | Percentual da advogada (%) | — |
| `{{ acordo_valor_fixo_de_honorarios }}` | Valor fixo de honorários (R$) | — |
| `{{ acordo_valor_advogada }}` | Valor da advogada (R$) | — |
| `{{ acordo_numero_de_parcelas }}` | Número de parcelas | — |
| `{{ acordo_data_primeira_parcela }}` | Data da 1ª parcela | — |
| `{{ acordo_valor_da_parcela }}` | Valor da parcela (R$) | — |
| `{{ acordo_total_advogada }}` | Total advogada (R$) | — |
| `{{ acordo_total_cliente }}` | Total cliente (R$) | — |

#### Data

| Placeholder | Descrição | Alias legado |
|-------------|-----------|--------------|
| `{{ data_hoje }}` | Data de hoje (dd/MM/yyyy) | — |
| `{{ data_hoje_extenso }}` | Data de hoje por extenso | — |

## Configuração

### Office Settings

Dados institucionais do escritório: OAB, CNPJ, endereço, logo, dados bancários e dias padrão de antecedência para alertas de prazos.

**Código automático:** `Office Settings`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Razão Social | Data | ✅ | Razão social do escritório. Usada em documentos gerados. |
| CNPJ | Data |  | CNPJ do escritório. Usado em contratos e documentos oficiais. |
| Registro SIA | Data |  | Registro no SIA/OAB do escritório. |
| Logo do Escritório | Attach Image |  | Logotipo exibido em documentos gerados (opcional). |
| Advogada(o) Principal | Data | ✅ | Nome da advogada responsável pelo escritório. |
| OAB | Data | ✅ | Número da OAB (apenas dígitos). |
| Dias padrão de antecedência (prazos) | Int |  | Dias padrão de antecedência para alertas de prazos. |
| Endereço Completo | Small Text | ✅ | Endereço completo do escritório para documentos. |
| Banco | Data |  | Nome do banco para dados em contratos e recibos. |
| Agência | Data |  | Agência bancária. |
| Conta | Data |  | Número da conta corrente. |
| Chave PIX | Data |  | Chave PIX para recebimentos. |

**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.

---

## Gestão de Documentos do Processo

### Upload manual

1. Abra o **Serviço** (Legal Case) ou use **+ Enviar** na aba **Documentos** do hub.
2. Preencha **Categoria**, **Status** e anexe o **Arquivo**.
3. Opcional: **Versão / Revisão** e **Prazo relacionado** (do mesmo serviço).

### Categorias disponíveis

Petição, Procuração, Certidão, Decisão, Contrato, Acordo, Substabelecimento, Comprovante, Protocolo, Laudo, Outro — cadastro em **Document Category**.

### Status e ciclo de vida

`Rascunho` → `Assinado` → `Protocolado` → `Juntado` (ou `Substituído` quando houver nova versão).

### Geração automática (.docx)

No **Serviço**, use **Gerar Documentos** ou **Gerar .docx** na aba Documentos. O sistema gera o Word, anexa ao serviço e cria um **Case Document** com origem **Gerado pelo App** e categoria inferida do nome do template.

### Onde localizar documentos

- **Hub do Serviço** — aba Documentos, pill 📄 Documentos na barra de resumo
- **Lista Case Document** — filtro por serviço ou cliente
- **Busca global** — pelo título composto ou ID `DOC-YYYY-####`

Documentação técnica: [case_documents.md](./case_documents.md)

---

## Navegação do Hub

### Breadcrumb

Ao abrir um registro satélite (prazo, documento, audiência, etc.) a partir do serviço, o topo do formulário exibe: **Serviço → Tipo de documento → Registro atual**.

### Voltar ao Serviço

Botão primário **Voltar ao Serviço** retorna ao Legal Case de origem.

### Abas e contagens

A barra de resumo no serviço mostra pills com contagem (audiências, prazos, documentos, …). Clique na pill para abrir a lista filtrada; use **+** para criar um novo registro.

Ao voltar de um satélite aberto pelo hub, a **mesma aba** (ex.: Documentos) é restaurada.

Documentação técnica: [hub_navigation.md](./hub_navigation.md)

---

## Fluxos Comuns

### Novo Processo
1. Cadastre o **Client**
2. Crie um **Serviço** com vara, comarca e tribunal
3. Defina **Acordo de Honorários** com parcelas
4. Cadastre **Audiências** e **Prazos**

### Recebimento
1. Registre **Legal Payment** quando o cliente pagar
2. O painel atualiza KPIs financeiros

---

*Regenerar: `bench execute advocacia.advocacia.scripts.generate_manual.generate`*