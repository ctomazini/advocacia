# Seção 7 — Preparação para IA

**App:** `advocacia` · **Status:** Fase 1 implementada · **Data:** 2026-06-02 · **Versão:** 1.0.0+

---

## 7.1 Estado atual

| Componente | Status |
|---|---|
| `agent_api.py` | ✅ Implementado (4 endpoints) |
| `test_agent_api.py` | ✅ 10 testes |
| Endpoints agregados para agente | ✅ Read-only |
| Documentação de contrato IA | ✅ Este arquivo + `docs/README.md` |
| REST `/api/resource/` em DocTypes | ✅ Nativo Frappe (24 DocTypes `custom: 0`) |
| Permissões role-aware | ✅ `setup/permissions.py` + redação financeira no summary |

O app está **operacional para humanos** e **pronto para integração MCP/Hermes** via endpoints agregados. Fase 2 (tools MCP registradas) permanece no backlog.

---

## 7.2 Superfície existente

### `agent_api.py` (Fase 1 — implementado)

| Função | Permission | Retorno |
|---|---|---|
| `get_active_cases` | Legal Case read | Lista casos `Em andamento` + `client_name`, contadores |
| `get_case_summary` | Legal Case read | Prazos, audiências, tarefas; financeiro condicional |
| `get_court_costs_by_type` | Manager + Court Cost read | Custas agregadas por tipo |
| `get_financial_overview` | Manager + Legal Payment read | Inadimplência e recebimentos do mês |

**Regras aplicadas:** read-only · `has_permission(..., throw=True)` · type hints · zero `commit()` · financeiro omitido para Advocacia User (espelha painel).

### Whitelists complementares (candidatos a tools MCP)

| Função | Módulo | Permission | Uso por agente |
|---|---|---|---|
| `get_painel_data` | painel_api.py | Legal Case read | Snapshot operacional do escritório |
| `legal_case_query` | legal_case.py | Legal Case read | Autocomplete processos |
| `gerar_documentos_em_lote` | documentos.py | Legal Case read | Gerar docx |
| `get_placeholders_referencia` | documentos.py | Document Template read | Referência de templates |
| `get_timer_ativo_usuario` | registro_de_horas.py | Time Entry read | Timer ativo |

---

## 7.3 Equivalência engenharia ↔ advocacia

| Engenharia | Advocacia |
|---|---|
| `get_active_projects` | `get_active_cases` |
| `get_project_summary` | `get_case_summary` |
| `get_costs_by_category` | `get_court_costs_by_type` |
| (implícito no summary) | `get_financial_overview` |

---

## 7.4 Payload exemplo — `get_case_summary`

```json
{
  "name": "LC-2026-0042",
  "title": "LC-2026-0042 — Silva Advogados Ltda",
  "client": "CLI-2026-0015",
  "client_name": "Silva Advogados Ltda",
  "status": "Em andamento",
  "deadlines": [],
  "hearings": [],
  "tasks": [],
  "fee_agreement_value": 15000.0,
  "amount_receivable": 3000.0,
  "pending_payments_count": +2,
  "court_costs_total": 850.0
}
```

Para **Advocacia User**, chaves financeiras são omitidas e `financial_restricted: true` é retornado.

---

## 7.5 Testes (`test_agent_api.py`)

| Teste | Assert |
|---|---|
| `test_get_active_cases_has_counts_and_client_name` | Contadores + `client_name` |
| `test_get_case_summary_financial_for_manager` | KPIs financeiros presentes |
| `test_get_case_summary_redacts_financial_for_user` | Sem valores para User |
| `test_get_court_costs_by_type` | Agregação por tipo |
| `test_get_court_costs_by_type_requires_manager` | PermissionError para User |
| `test_permission_denied_without_access` | PermissionError sem role |

---

## 7.6 Roadmap restante

### Fase 2 — Tools MCP

1. Registrar tools espelhando `agent_api.py`.
2. OpenAPI ou docstring estruturada exportável.
3. Smoke com Cursor MCP ou script `xcall`.

### Fase 3 — Write controlado (futuro)

1. Endpoints para criar Prazo/Legal Task com validação server-side.
2. Confirmação em duas etapas para ações financeiras.
3. Audit trail via `track_changes` nos DocTypes.

---

## 7.7 Segurança

| Risco | Mitigação |
|---|---|
| Vazamento honorários para User | Endpoints financeiros só Manager |
| Agente com credencial Administrator | Documentar — usar role dedicada |
| Dados demo `_DEMO_` em produção | Proibir `seed-demo` em prod |
| CPF/CNPJ em prompts | API retorna mascarado nos placeholders docx |

---

*Atualizado pós-implementação Fase 1 (jun/2026). Ver também [crosscheck_engenharia.md](./crosscheck_engenharia.md).*
