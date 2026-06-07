# Seção 7 — Preparação para IA (Pós-deploy)

**App:** `advocacia` · **Status:** planejado · **Data:** 2026-06-02 · **Versão alvo:** pós v0.7.0

---

## 7.1 Estado atual

| Componente | Status v0.7.0 |
|---|---|
| `agent_api.py` | ❌ Não existe |
| `test_agent_api.py` | ❌ Não existe |
| Endpoints agregados para agente | ❌ |
| Documentação de contrato IA | ✅ Este arquivo |
| REST `/api/resource/` em DocTypes | ✅ Nativo Frappe (24 DocTypes `custom: 0`) |
| Permissões role-aware | ✅ `setup/permissions.py` + `strip_financial_payload` |

O app está **operacional para humanos** e **parcialmente pronto para agentes** via REST genérico. Falta camada de conveniência read-only otimizada para LLM/MCP.

---

## 7.2 Superfície existente utilizável hoje

### Whitelists já seguros (candidatos a tools MCP)

| Função | Módulo | Permission | Uso por agente |
|---|---|---|---|
| `get_painel_data` | painel_api.py | Legal Case read | Snapshot operacional do escritório |
| `servico_query` | servico.py | Legal Case read | Autocomplete processos |
| `get_resumo_audiencia` | audiencia.py | Hearing read | Detalhe audiência |
| `get_resumo_prazo` | controle_de_prazos.py | Deadline read | Detalhe prazo |
| `generate_document` | documentos.py | Legal Case read | Gerar docx |
| `get_timer_ativo_usuario` | registro_de_horas.py | Time Entry read | Timer ativo |

### REST CRUD (Frappe nativo)

DocTypes expõem CRUD com DocPerm. **Advocacia User** não cria `Legal Payment` — agente com credencial User herda essa restrição.

---

## 7.3 Endpoints planejados (`agent_api.py`)

Módulo sugerido: `advocacia/advocacia/agent_api.py`  
Facade pattern igual ao painel — único path de `xcall`.

| Função proposta | Parâmetros | Permission | Retorno |
|---|---|---|---|
| `get_active_servicos` | `status=None`, `limit=20` | Legal Case read | Lista `{name, title, cliente, status, fase}` |
| `get_servico_summary` | `servico` | Legal Case read | Resumo: prazos abertos, próxima audiência, tarefas pendentes |
| `get_servico_financial_summary` | `servico` | **Manager only** | Honorários, parcelas vencidas, custas — ou 403 para User |
| `get_deadlines_due` | `days=7`, `servico=None` | Deadline read | Prazos no período |
| `get_upcoming_audiencias` | `days=7`, `servico=None` | Hearing read | Audiências no período |

### Regras de desenho

1. **Read-only** — agente não altera dados nesta fase.
2. **`has_permission(..., throw=True)`** em todo endpoint.
3. **Type hints** em todas as assinaturas.
4. **Zero N+1** — batch lookups como `painel/_helpers.py`.
5. **Zero `commit()`** no módulo.
6. **Financeiro condicional** — versão User omite valores (espelhar `strip_financial_payload`).

---

## 7.4 Gaps para agente IA (MCP / assistente)

| Operação | Possível hoje? | Gap |
|---|---|---|
| Listar processos ativos | 🟡 REST GET Legal Case | Sem agregação; precisa filtros manuais |
| Resumo de um processo | 🟡 Múltiplos GETs | Sem endpoint único |
| Prazos da semana | 🟡 REST GET Deadline | Sem whitelist dedicado |
| Honorários pendentes | 🟡 Manager REST Legal Payment | User bloqueado — correto |
| Gerar petição/docx | ✅ `documentos.generate_document` | — |
| Criar prazo | ✅ REST POST | Agente precisa write + validação datas |
| Marcar parcela recebida | ✅ `painel_api.marcar_parcela_recebida` | Requer Manager/write Legal Payment |
| Consultar carteira | 🟡 Report `carteira_ativa` | Sem API JSON dedicada |
| Timer horas | ✅ whitelisted | — |

---

## 7.5 Schema / DX para LLM

| Item | Ação planejada |
|---|---|
| OpenAPI ou docstring estruturada | Gerar a partir de `agent_api.py` |
| Exemplos de payload | Incluir em `docs/` após implementação |
| Lista estável de chaves JSON | Versionar — não renomear sem bump |
| System prompt do escritório | Template com roles Advocacia User/Manager |

### Payload exemplo (planejado) — `get_servico_summary`

```json
{
  "servico": "SERV-2026-0042",
  "title": "SERV-2026-0042 — Silva Advogados Ltda",
  "cliente": "CLI-2026-0015",
  "cliente_nome": "Silva Advogados Ltda",
  "status": "Em andamento",
  "prazos_abertos": 3,
  "proxima_audiencia": "2026-06-10 14:00:00",
  "tarefas_pendentes": 2,
  "is_manager": false,
  "financeiro": null
}
```

---

## 7.6 Testes planejados (`test_agent_api.py`)

| Teste | Assert |
|---|---|
| `test_get_active_servicos` | Retorna lista com title |
| `test_get_servico_summary` | Chaves estáveis |
| `test_user_no_financial_summary` | `financeiro` ausente ou null |
| `test_manager_financial_summary` | Valores presentes |
| `test_permission_denied_guest` | PermissionError |

Estimativa: 8–12 métodos. Suite total passaria de 230 para ~242.

---

## 7.7 Segurança e privacidade

| Risco | Mitigação |
|---|---|
| Vazamento honorários para User | `get_servico_financial_summary` só Manager |
| Agente com credencial Administrator | Documentar — usar role dedicada |
| Dados demo `_DEMO_` em produção | Proibir `seed-demo` em prod |
| CPF/CNPJ em prompts | API retorna dígitos — mascarar no client do agente |
| Log de chamadas IA | Futuro: `Communication` tipo "Sistema" |

---

## 7.8 Roadmap de implementação

### Fase 1 — Read-only (1–2 dias)

1. Criar `agent_api.py` com 3 endpoints mínimos.
2. `test_agent_api.py` + `has_permission` em todos.
3. Documentar chaves neste arquivo (seção 7.5).

### Fase 2 — Tools MCP (2–3 dias)

1. Registrar tools espelhando `agent_api.py`.
2. Smoke com Cursor MCP ou script `xcall`.
3. Avaliar cache de `get_painel_data` vs endpoints granulares.

### Fase 3 — Write controlado (futuro)

1. Endpoints para criar Prazo/Legal Task com validação server-side.
2. Confirmação em duas etapas para ações financeiras.
3. Audit trail via `track_changes` nos DocTypes.

---

## 7.9 Referência cruzada

| App | Implementação |
|---|---|
| Engenharia | `agent_api.py` (3 endpoints) + `test_agent_api.py` + este padrão de doc |
| Advocacia v0.7.0 | Painel modular + permissions — base pronta; falta `agent_api` |

**Equivalente jurídico fechado:**
- `get_active_servicos` ↔ `get_active_projects`
- `get_servico_summary` ↔ `get_project_summary`
- `get_servico_financial_summary` ↔ custos/honorários (Manager)

---

*Documento normativo para planejamento pós-deploy v0.7.0. Implementação de `agent_api.py` é pré-requisito para integração MCP/Hermes.*
