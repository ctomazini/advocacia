# Seção 6 — Integração Google Calendar

**App:** `advocacia` · **Módulo:** `calendar_sync.py` · **Frappe:** v16.19.0 · **Data:** 2026-06-02

---

## 6.1 Estado atual no app advocacia

### Sincronização implementada

| DocType | Eventos `hooks.py` | Função | Destino |
|---|---|---|---|
| **Audiencia** | `after_insert`, `on_update` | `sync_audiencia_to_event` | `Event` nativo Frappe |
| **Controle de Prazos** | `after_insert`, `on_update` | `sync_prazo_to_event` | `Event` nativo Frappe |

**Não sincronizam:** Tarefa, Comunicacao, Pagamento, Registro de Horas.

### Mapeamento Audiencia → Event

| Campo Event | Origem |
|---|---|
| `subject` | `_audiencia_subject(doc)` — tipo + cliente + serviço |
| `starts_on` | `data_hora` |
| `ends_on` | `starts_on + 2 horas` |
| `event_type` | `Public` |
| `description` | Comarca, vara, modalidade, observações |
| `custom_source_doctype` | `"Audiencia"` |
| `custom_source_name` | `doc.name` |

**Cancelamento:** se `status_aud == "Cancelada"` → Event `status = Closed`.

### Mapeamento Controle de Prazos → Event

| Campo Event | Origem |
|---|---|
| `subject` | `PRAZO: {descricao}` |
| `starts_on` | `data_prazo` |
| `all_day` | `1` |
| `color` | `red` (Alta), `orange` (Média), `blue` (demais) |
| `description` | Serviço, cliente, prioridade, status |
| `custom_source_doctype` | `"Controle de Prazos"` |
| `custom_source_name` | `doc.name` |

**Cancelamento:** se `status == "Concluído"` → Event `status = Closed`.

### Custom Fields em Event

Fixtures + `after_migrate`:
- `custom_source_doctype` (Link/Data)
- `custom_source_name` (Data)

Permitem idempotência: `_find_linked_event(source_doctype, source_name)`.

### Permissões na sync

```python
event.save(ignore_permissions=True)   # sistema sincroniza Event em nome do usuário
event.insert(ignore_permissions=True)
```

Justificativa documentada inline — padrão §9 do `REGRAS_ADVOCACIA.md`.

---

## 6.2 Testes

**Arquivo:** `test_calendar_sync.py` (6 métodos)

| Cenário | Coberto |
|---|---|
| Audiencia cria Event | ✅ |
| Audiencia atualiza Event existente | ✅ |
| Audiencia cancelada fecha Event | ✅ |
| Prazo cria Event all_day | ✅ |
| Prazo concluído fecha Event | ✅ |
| Cor por prioridade | ✅ |

**Não coberto:** OAuth Google, sync bidirecional, múltiplos calendários por usuário.

---

## 6.3 Google Calendar API no Frappe v16

### Infraestrutura nativa (bench)

| Item | Status |
|---|---|
| DocType `Google Calendar` | ✅ Frappe core (`frappe/integrations/doctype/google_calendar/`) |
| OAuth Google | ✅ `GoogleOAuth`, scope `calendar` |
| Sync bidirecional | ✅ Event ↔ Google Calendar (por usuário) |
| advocacia chama Google diretamente? | ❌ — apenas via Event |

### Fluxo recomendado para produção

```
Audiencia / Controle de Prazos
        ↓ calendar_sync.py
    Event (Frappe desk)
        ↓ Google Calendar settings (por usuário)
    Google Calendar (nuvem)
```

**Esforço setup OAuth admin:** ~0,5–1 dia (Google Cloud Console + DocType por usuário).

---

## 6.4 Calendar View custom

| Item | Status |
|---|---|
| `doctype_calendar_js` em hooks | ❌ não configurado |
| DocTypes com `calendar.js` próprio | 0 |
| Usuário vê Events no desk | ✅ Calendar nativo Frappe |

Prazos e audiências aparecem no calendário **indiretamente** via Event — não via Calendar View do DocType jurídico.

---

## 6.5 Alternativas avaliadas

| Abordagem | Prós | Contras | Esforço |
|---|---|---|---|
| **A) Event + Google Calendar nativo** | Zero código extra; OAuth pronto | Usuário configura sync; Tarefas fora | 🟢 Baixo |
| **B) CalDAV** | Padrão aberto | Frappe sem CalDAV built-in | 🔴 Alto |
| **C) API `google-api-python-client` custom** | Controle total | Duplica OAuth Frappe | 🟡 Médio-alto |
| **D) Webhook outbound** | Integrações externas | Infra adicional | 🟡 Médio |

**Recomendação:** 🟢 **Opção A** — manter `calendar_sync.py` e documentar setup Google Calendar no manual do escritório.

---

## 6.6 Gaps e roadmap

| Gap | Severidade | Esforço estimado |
|---|---|---|
| Tarefa → Event | 🟡 | 1 dia dev |
| Sync seletivo por serviço/cliente | 🔴 | Não implementado |
| Notificação push Google | 🟢 | Depende do sync nativo Frappe |
| Documentação admin OAuth | 🟡 | 2–4h docs |

### Extensão sugerida: Tarefa → Event

Espelhar `sync_prazo_to_event`:
- `starts_on` = `data_limite`
- `subject` = `TAREFA: {titulo}`
- Cancelar se `status == "Concluída"`

---

## 6.7 Checklist deploy calendário

- [ ] `bench --site <site> migrate` — Custom Fields em Event
- [ ] Criar Google Calendar DocType por advogado/usuário
- [ ] Testar: criar Audiencia → ver Event no desk
- [ ] Testar: conectar Google → evento aparece no app Google Calendar
- [ ] `run-tests --app advocacia` — `test_calendar_sync.py` verde

---

*Paridade estrutural com app `engenharia` (Deadline/Permit → Event). Domínio jurídico: Audiencia + Controle de Prazos.*
