# CODEBASE.md — App Advocacia (Frappe v16)

**Fonte:** `advocacia/advocacia/` + `advocacia/hooks.py`  
**Repositório:** https://github.com/ctomazini/advocacia  
**Branch auditada:** `frappe-v16`  
**Data da auditoria:** 2026-05-29

---

## 1. Inventário de Arquivos

Escopo principal: `advocacia/advocacia/` — arquivos `.py`, `.js` e `.json` (exclui `__init__.py` vazios salvo menção).

### 1.1 Python

| Path | Propósito | Exporta | Dependências / Links |
|------|-----------|---------|----------------------|
| `advocacia/advocacia/painel_api.py` | API do Painel (KPIs, parcelas, prazos, tarefas, audiências) | `get_painel_data()` | `frappe`, `Servico`, `Cliente`, `Parcela de Honorarios`, `Controle de Prazos`, `Tarefa`, `Audiencia`, `Acordo de Honorarios Processuais` |
| `advocacia/advocacia/notificacoes.py` | Scheduler diário de prazos + função órfã de “Fatura” | `notificar_prazos_diario()`, `atualizar_status_faturas()` | `Controle de Prazos`, `Has Role`, `Fatura` (DocType inexistente no app) |
| `advocacia/advocacia/documentos.py` | Geração de .docx a partir de template | `gerar_documento()`, `get_templates_disponiveis()`, `_formatar_data_extenso()` | `docxtpl`, `Servico`, `Cliente`, `Template Documento`, `File` |
| `advocacia/advocacia/setup.py` | Pós-migrate: reimporta child DocTypes se ausentes | `reinstalar_istable_doctypes()`, `ISTABLE_DOCTYPES` | `frappe.modules.import_file` |
| `doctype/cliente/cliente.py` | Limpa campos PF/PJ no save | `Cliente` | `Document` |
| `doctype/parcela_de_honorarios/parcela_de_honorarios.py` | Status automático + ações whitelisted | `ParceladeHonorarios`, `registrar_recebimento()`, `registrar_repasse()` | `today()` |
| `doctype/tarefa/tarefa.py` | Data conclusão + concluir | `Tarefa`, `concluir()` | `today()` |
| `doctype/acordo_de_honorarios_processuais/acordo_de_honorarios_processuais.py` | Stub | `AcordodeHonorariosProcessuais` | — |
| `doctype/servico/servico.py` | Stub | `Servico` | — |
| `doctype/audiencia/audiencia.py` | Stub | `Audiencia` | — |
| `doctype/controle_de_prazos/controle_de_prazos.py` | Stub | `ControledePrazos` | — |
| `doctype/registro_de_atos/registro_de_atos.py` | Stub | `RegistrodeAtos` | — |
| `doctype/ato_advocaticio/ato_advocaticio.py` | Stub | `AtoAdvocaticio` | — |
| `doctype/contato_cliente/contato_cliente.py` | Stub | `ContatoCliente` | — |
| `doctype/endereco_cliente/endereco_cliente.py` | Stub | `EnderecoCliente` | — |
| `doctype/template_documento/template_documento.py` | Stub | `TemplateDocumento` | — |

### 1.2 JavaScript

| Path | Propósito | Exporta | Dependências |
|------|-----------|---------|--------------|
| `page/painel/painel.js` | Page Painel (KPIs, listas) | `frappe.pages['painel']`, helpers | `painel_api.get_painel_data` |
| `public/js/navegacao.js` | FAB “Painel”, botão header, CalendarView Audiência/Prazos | IIFE global | Vários DocTypes |
| `public/js/servico.js` | Botão “Gerar Documento” no Serviço | `frappe.ui.form.on('Servico')` | `documentos.*` |
| `documentos_client.js` | Duplicata de `public/js/servico.js` | Idem | Idem |
| `doctype/acordo_de_honorarios_processuais/acordo_de_honorarios_processuais.js` | UX + validação financeira no cliente + geração de parcelas | `calcular_*`, `validar_tudo`, `gerar_tabela_parcelas` | Child `Parcela de Honorarios` (`table_ztjx`) |
| `doctype/registro_de_atos/registro_de_atos.js` | Totais/status no cliente + cobrança | `calcular_totais_atos`, `gerar_cobranca_atos` | Server Script API `gerar_faturas_atos` |
| `doctype/parcela_de_honorarios/parcela_de_honorarios.js` | Indicadores + botões recebimento/repasse | — | métodos no doc |
| `doctype/servico/servico.js` | Atalhos criar Acordo/Prazo/Audiência | — | — |
| `doctype/audiencia/audiencia.js` | Botão entrar (virtual) + limpar link | — | — |
| `doctype/tarefa/tarefa.js` | Indicador + concluir | — | `concluir` no doc |

### 1.3 JSON (não-DocType)

| Path | Propósito |
|------|-----------|
| `fixtures/client_script.json` | Client Script “Navegacao Advocacia” (inline JS) |
| `fixtures/custom_field.json` | Custom Fields ERPNext: `Sales Invoice-custom_servico`, `Customer-custom_*` |
| `fixtures/server_script.json` | 4 Server Scripts API (faturas acordo/atos) |
| `fixtures/workspace.json` | Workspace “Advocacia” (export com URLs de produção) |
| `custom_fields_export.json` | Subconjunto: só `Sales Invoice-custom_servico` |
| `server_scripts_export.json` | Export alternativo de server scripts |
| `workspace/advocacia/advocacia.json` | Workspace canônico (links para DocTypes do app) |

### 1.4 DocTypes

12 DocTypes em `doctype/`: 8 principais + 4 child (`istable=1`).

---

## 2. Mapa de DocTypes

Legenda hooks Python: nenhum DocType tem `validate`/`on_update` no `.py` exceto `Cliente.before_save`, `Parcela.before_save` e `Tarefa.before_save`.

**calendar.js:** não existe em pastas de DocType; calendário está em `public/js/navegacao.js`.

### 2.1 Cliente

| fieldname | fieldtype | label | options (Link) |
|-----------|-----------|-------|----------------|
| tipo_pessoa | Select | Tipo de Pessoa | — |
| nome | Data | Nome / Razão Social | — |
| nome_fantasia | Data | Nome Fantasia | — |
| cpf | Data | CPF | — |
| rg | Data | RG | — |
| cnpj | Data | CNPJ | — |
| nacionalidade, estado_civil, profissao | Data/Select | — | — |
| representante, cpf_representante, cargo_representante, nacionalidade_pj | Data | — | — |
| contatos | Table | Contatos | Contato Cliente |
| enderecos | Table | Endereços | Endereco Cliente |
| observacoes | Text Editor | Observações | — |

- **autoname:** `field:nome` | **custom:** 0 | **istable:** 0
- **Permissões:** System Manager, All (sem Advocacia User/Manager)
- **.py:** `before_save` (limpa campos PF/PJ)
- **.js:** não | **calendar.js:** não

### 2.2 Servico

| fieldname | fieldtype | label | options |
|-----------|-----------|-------|---------|
| cliente | Link | Cliente | Cliente |
| tipo | Select | Tipo | Processo Judicial, Consultoria, … |
| title | Data | Título | — |
| status | Select | Status | Em andamento, Encerrado, Suspenso |
| data_abertura | Date | Data de Abertura | — |
| numero_processo | Data | Número do Processo | — (deveria ser CNJ validado) |
| area | Select | Área | Família, Trabalhista, … |
| vara | Data | Vara | — (cadastro rígido pendente) |
| comarca | Data | Comarca | — (cadastro rígido pendente) |
| parte_contraria | Data | Parte Contrária | — |
| valor_causa | Currency | Valor da Causa | — |
| observacoes | Text Editor | Observações | — |

- **autoname:** `format:SERV-{####}` | **custom:** 0
- **Permissões:** System Manager, Projects Manager, Projects User
- **.py:** stub | **.js:** atalhos | **doctype_js (hooks):** `public/js/servico.js`
- **Links:** Acordo, Registro de Atos, Audiencia, Controle de Prazos, Sales Invoice

### 2.3 Acordo de Honorarios Processuais

Campos principais: `servico`→Servico, `cliente`→Cliente (fetch), `modo_honorarios`, `status` (Vigente/Encerrado/Cancelado), valores/percentuais/sucumbência, `table_ztjx`→Parcela de Honorarios, totais, observações.

- **autoname:** `format:ACOR-{####}` | **custom:** 0
- **Permissões:** System Manager, Projects Manager, Projects User
- **.py:** stub | **.js:** cálculos, geração parcelas, `validate` no JS

### 2.4 Parcela de Honorarios (child)

`vencimento`, `valor_total`, `valor_advogada`, `valor_sucumbência`, `valor_cliente`, `descrição` (Small Text), `status` (Pendente/Vencida/Recebida/Repassada/Cancelada), `data_recebimento`, `data_repasse`, `forma_recebimento`, `observacao`.

- **istable:** 1 | **permissions:** `[]`
- **.py:** `before_save` → `atualizar_status()`; whitelisted `registrar_recebimento`, `registrar_repasse`

### 2.5 Registro de Atos

`servico`, `cliente` (fetch), `status`, `data_abertura`, `atos`→Ato Advocaticio, totais, `gerar_cobranca` (Button).

- **autoname:** `format:ATOS-{####}`
- **.js:** totais/status + chama `gerar_faturas_atos`

### 2.6 Ato Advocaticio (child)

`data`, `tipo` (Select), `descrição`, `valor`, `status` (Pendente/Cobrado).

### 2.7 Controle de Prazos

`servico`, `cliente` (fetch), `data_prazo`, `status`, `descricao`, `prioridade`, `responsavel`→User, `dias_notificacao` (default 3), `observacoes`.

- **autoname:** `format:PRAZO-{####}`

### 2.8 Audiencia

`servico`, `cliente`, `data_hora`, `status_aud`, `tipo`, `modalidade`, `link_virtual`, `local_vara` (Data), `resultado`, `observacoes`.

- **autoname:** `format:AUD-{####}`

### 2.9 Tarefa

`naming_series`, `titulo`, `status`, `prioridade`, `data_limite`, `descricao`, `servico`, `responsavel`, `data_conclusao`.

- **autoname:** `naming_series:` `TAR-.YYYY.-`
- **Permissões:** System Manager, All

### 2.10 Template Documento

`titulo` (autoname), `tipo_documento`, `descricao`, `habilitado`, `arquivo`, `placeholders_info` (HTML).

### 2.11 Contato Cliente / Endereco Cliente (child)

**Contato Cliente:** `nome`, `tipo`, `telefone`, `celular`, `email`, `observacao` — todos Data.

**Endereco Cliente:** `tipo`, `cep`, `logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `estado` (Select UF), `principal`.

---

## 3. hooks.py

**Arquivo:** `advocacia/hooks.py`

| Hook | Valor | Existe no FS? |
|------|-------|----------------|
| `fixtures` | Workspace “Advocacia”; Client Script “Link Audiencia Virtual” | Nome do script no fixture é “Navegacao Advocacia” — possível dessincronia no import |
| `doctype_js` | `Servico` → `public/js/servico.js` | Sim (`advocacia/advocacia/public/js/servico.js`) |
| `app_include_js` | `/assets/advocacia/js/navegacao.js` | Sim (build a partir de `public/js/navegacao.js`) |
| `scheduler_events.daily` | `advocacia.advocacia.notificacoes.notificar_prazos_diario` | Sim |
| `after_migrate` | `advocacia.advocacia.setup.reinstalar_istable_doctypes` | Sim |

**Não registrados (esperados pelas regras do projeto):**

- `doc_events` (ex.: `Parcela de Honorarios.on_update`)
- Schedulers: `verificar_parcelas_vencidas`, `verificar_audiencias`
- Fixtures: Custom Field, Server Script, Role, Property Setter
- Regras citam `notificacoes.verificar_prazos` — não existe; só `notificar_prazos_diario`

---

## 4. Fixtures

| Arquivo | Conteúdo | Sincronização |
|---------|----------|----------------|
| `fixtures/workspace.json` | Workspace com links a Customer, Sales Invoice, URLs `erp.carinepageladvocacia.com.br` | Diverge de `workspace/advocacia/advocacia.json` |
| `fixtures/client_script.json` | Script FAB Painel (lista inclui Sales Invoice/Customer) | Pode conflitar com `navegacao.js` |
| `fixtures/custom_field.json` | 5 Custom Fields em Customer + Sales Invoice | Não está em `hooks.fixtures` |
| `fixtures/server_script.json` | APIs faturas acordo/atos | Não está em hooks; status parcela usa `"Pago"` inexistente |
| `custom_fields_export.json` | Apenas `custom_servico` | Redundante |

**Banco:** comparar com `bench --site advocacia.local export-fixtures` e datas `modified` nos JSON.

---

## 5. APIs

### 5.1 Python (`@frappe.whitelist`)

| Método | Módulo | Parâmetros | Retorno | Permissão? |
|--------|--------|------------|---------|------------|
| `get_painel_data` | `painel_api` | — | dict (listas + `totais`) | Não |
| `gerar_documento` | `documentos` | `servico_name`, `template_name` | `{file_url, file_name}` | Não |
| `get_templates_disponiveis` | `documentos` | — | lista Template Documento | Não |
| `registrar_recebimento` | `parcela_de_honorarios` | doc | `{status}` | Via doc |
| `registrar_repasse` | parcela | doc | `{status}` | Via doc |
| `concluir` | `tarefa` | doc | `{status}` | Via doc |

**`get_painel_data`:** enriquece parcelas/prazos/tarefas/audiências; usa `` `descrição` `` em fields; `futuras` com `limit_page_length=0`; `except Exception: pass` silencioso no cache de acordo.

### 5.2 Server Scripts (fixtures)

| API | Função |
|-----|--------|
| `gerar_faturas_acordo` | Cria Sales Invoice por parcela (`status != "Pago"`) |
| `atualizar_faturas_acordo` | Apaga e recria faturas |
| `contar_faturas_acordo` | Contagens por remarks `ACOR:{name}` |
| `gerar_faturas_atos` | Uma fatura + marca atos Cobrado |

Todas usam `ignore_permissions=True` no insert.

---

## 6. Problemas Encontrados

### Críticos

1. **Painel sem container:** `painel.js` usa `getElementById('painel-root')` mas não cria `#painel-root` no `on_page_load`.
2. **Duplicação de Page:** `advocacia/page/painel/painel.js` vs `advocacia/advocacia/page/painel/painel.js`; `painel.json` só na pasta pai.
3. **`documentos.py`** referencia `cliente.celular`, `cliente.telefone`, `cliente.email` — não existem no JSON de Cliente.
4. **Server Scripts:** filtro `parcela.status == "Pago"` — opções reais: Pendente/Vencida/Recebida/…
5. **`atualizar_status_faturas()`** referencia DocType `Fatura` inexistente.
6. **Fixture Client Script:** filtro `Link Audiencia Virtual` ≠ nome `Navegacao Advocacia`.

### Arquitetura / `.cursorrules`

7. Cadastro rígido: `comarca`, `vara`, `local_vara` como Data; sem Comarca/Vara/Tribunal/Fase Processual.
8. CNJ: `numero_processo` sem validação Módulo 97 no Python.
9. CPF/CNPJ/telefones: sem limpeza numérica nem DV no servidor.
10. Lógica de negócio no JS: `acordo_*.js`, `registro_de_atos.js`.
11. Sem máscaras `jquery.inputmask` nos forms.
12. Sem roles `Advocacia User` / `Advocacia Manager`.
13. Painel: cores hex hardcoded; retorno API não segue `{success, data, message}`.
14. Calendário sem `get_events` Python; sem `calendar.js` por DocType.
15. Automações incompletas: scheduler parcelas, notificações audiência/parcela, `doc_events`, status acordo Quitado.
16. `get_painel_data`: `limit_page_length=0` em futuras.
17. Código duplicado: `documentos_client.js`, navegação fixture vs `navegacao.js`, pastas duplicadas em `advocacia/` raiz.
18. Fieldnames com acentos: `descrição`, `honorários_de_sucumbência`.
19. Acordo `status` sem “Quitado”.

---

## 7. Dívida Técnica

### P0 — Estabilidade

- Corrigir Painel (`page.main` + container ou equivalente).
- Unificar `painel.js` + `painel.json` em `advocacia/advocacia/page/painel/`.
- Alinhar `documentos.py` com contatos do Cliente.
- `frappe.has_permission` / `only_for` em APIs do painel e documentos.
- Registrar fixtures (`custom_field`, `server_script`) ou remover dependência.

### P1 — Domínio jurídico

- Módulo Python: CNJ, CPF, CNPJ, telefone ANATEL; `before_save` nos DocTypes.
- DocTypes: Comarca, Vara, Tribunal, Fase Processual.
- Mover validação do Acordo e totais do Registro de Atos para Python.

### P2 — Automação end-to-end

- `scheduler_events`: parcelas vencidas, audiências; `doc_events` Parcela → Acordo Quitado.
- DocType `Notification` nativo.
- `get_events` + `calendar.js` por DocType.

### P3 — UX / design system

- Refatorar `painel.js` com variáveis CSS Frappe e loading state.
- Máscaras em `refresh`.
- Roles Advocacia e permissions nos DocTypes.
- Fieldnames em inglês; export fixtures antes de commits.

---

## Apêndice — Árvore `advocacia/advocacia/`

```
advocacia/advocacia/
├── painel_api.py, notificacoes.py, documentos.py, setup.py
├── documentos_client.js
├── custom_fields_export.json, server_scripts_export.json
├── fixtures/ (client_script, custom_field, server_script, workspace)
├── workspace/advocacia/advocacia.json
├── public/js/ (navegacao.js, servico.js)
├── page/painel/painel.js
└── doctype/
    ├── cliente, servico, acordo_de_honorarios_processuais
    ├── parcela_de_honorarios, registro_de_atos, ato_advocaticio
    ├── controle_de_prazos, audiencia, tarefa, template_documento
    ├── contato_cliente, endereco_cliente
```

---

*Gerado por auditoria estática do branch `frappe-v16`. Para validar fixtures vs banco: `bench --site advocacia.local export-fixtures --app advocacia`.*
