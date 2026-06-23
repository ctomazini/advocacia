# Seção 5 — Layout de formulários (Column Breaks)

**App:** `advocacia` · **Data:** 2026-06-23 · **Versão:** 1.1.0  
**Escopo:** todos os DocTypes **exceto** `Legal Case` (hub com abas próprias).

---

## 5.1 Regra adotada

| Tipo de campo | Layout |
| --- | --- |
| Link, Select, Data, Date, Currency, Check, Int | Preferir **2 colunas** na mesma seção |
| Text Editor, Small Text longo, Table | **Largura total** (sem Column Break adjacente) |
| Seções colapsáveis | Observações / anexos quando possível lado a lado |
| Cadastros auxiliares (3 campos) | Uma Column Break no meio |

**Referência de bom layout:** `Deadline`, `Hearing`, `Office Expense`, `Fee Agreement`.

---

## 5.2 Alterações (jun/2026)

| DocType | Antes | Depois |
| --- | --- | --- |
| **Client** | Dados PF em coluna única | `nationality` \| `marital_status` + `occupation` |
| **Legal Payment** | Origem e Controle 1 coluna | `installment_origin_id` \| `synced_at` + `manual_override`; `remarks` \| `receipt` |
| **Legal Task** | Text Editor + coluna ao lado | `responsible` + `completion_date` na seção Informações; `description` full-width |
| **Case Communication** | Próximos passos 1 coluna | `next_steps` \| `generate_task` + `legal_task` |
| **Service Record** | Cobrança 1 coluna; Totais 3 colunas | Cobrança 2 col; Totais 2 col (`pending` \| `billed` + `grand_total`) |
| **Time Entry** | Atividade linear | `activity` + `category` \| `billable`; `description` full-width |
| **Court Cost** | Comprovante + seção Obs separadas | Seção **Controle**: `receipt` \| `remarks` |
| **Jurisdiction** | 3 campos empilhados | `jurisdiction_name` \| `uf` + `city` |
| **Court Branch** | 3 campos empilhados | `court_branch_name` \| `jurisdiction` + `court_type` |
| **Court** | 3 campos empilhados | `court_name` + `abbreviation` \| `jurisdiction` |

### Já adequados (sem mudança)

`Deadline`, `Hearing`, `Office Expense`, `Fee Agreement`, `Document Template`, `Document Kit`, `Office Settings`, `Case Phase`.

### Fora de escopo

`Legal Case` — layout por abas (`tab_details`, `tab_financial`, …) no hub.

---

## 5.3 Manutenção

Após editar JSON de DocType:

```bash
bench --site advocacia.local migrate
bench --site advocacia.local clear-cache   # se alterar JS de form
```

Ao adicionar campos novos em satélites transacionais, seguir o padrão 2 colunas da seção **Informações** de `Deadline` / `Hearing`.

---

*Complementa [audit_usability.md](./audit_usability.md) §3.6.*

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
