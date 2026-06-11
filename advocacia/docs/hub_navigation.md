# Navegação hub ↔ satélites

Guia técnico da navegação entre **Legal Case** (hub / Serviço) e DocTypes satélite.

Operador: ver seção *Navegação do Hub* em [manual_usuario.md](./manual_usuario.md).

---

## Arquivo principal

`advocacia/public/js/adv_case_nav.js` — incluído globalmente via `hooks.py` (`app_include_js`), **antes** de `case_hub.js`.

---

## DocTypes cobertos

**Hub:** `Legal Case`

**Satélites (10):**

| DocType | Campo de vínculo |
| --- | --- |
| Case Document | `legal_case` |
| Deadline | `legal_case` |
| Fee Agreement | `legal_case` |
| Hearing | `legal_case` |
| Court Cost | `legal_case` |
| Service Record | `legal_case` |
| Case Communication | `legal_case` |
| Time Entry | `legal_case` |
| Legal Task | `legal_case` |
| Legal Payment | `legal_case` |

Campo padrão: `legal_case`. Exceções em `CASE_FIELD_BY_DOCTYPE` (vazio hoje — reservado para futuros DocTypes).

Lista canônica: `SATELLITE_DOCTYPES` em `adv_case_nav.js`.

---

## Funcionalidades

### Breadcrumb

Renderizado no `<ul class="navbar-breadcrumbs">` do formulário ativo (patch de `frappe.breadcrumbs.update`).

Cadeia típica em satélite:

`Home → Workspace → {ID serviço} → {DocType} → {ID documento}`

- Crumbs do serviço e do registro usam **somente o ID** (`SERV-…`, `DOC-…`), não o título composto.
- Formulário do próprio Legal Case não exibe crumb duplicado do serviço.

### Voltar ao Serviço

Botão primário **Voltar ao Serviço** em todos os satélites (exceto registro novo sem `legal_case`).

### Restaurar aba do hub

Antes de sair do Legal Case via hub, o contexto é salvo em `sessionStorage`. Ao retornar, a aba ativa é reaberta.

**Chave:** `adv_hub_return_context`

**Payload JSON:**

```json
{
  "legal_case": "SERV-2026-0042",
  "tab": "tab_documents"
}
```

Abas conhecidas no Legal Case:

| fieldname | Conteúdo |
| --- | --- |
| `tab_details` | Dados gerais |
| `tab_progress` | Fases e audiências |
| `tab_financial` | Financeiro (honorários, pagamentos, cobranças de serviços, custas) |
| `tab_deadlines` | Prazos e tarefas |
| `tab_records` | Comunicações e registro de horas |
| `tab_documents` | Documentos e kits |

Default se nenhuma aba detectada: `tab_details`.

---

## Helpers globais

| Função | Uso |
| --- | --- |
| `adv_case_nav_follow_route(route_str)` | Navega `Form/DocType/name` preservando contexto da aba |
| `adv_case_nav_new_doc(doctype, defaults)` | Novo satélite com defaults |
| `adv_case_nav_set_route(...)` | Wrapper de `frappe.set_route` |
| `adv_case_nav_restore_tab(frm)` | Restaura aba (refresh do Legal Case) |

Objeto exposto: `window.adv_case_nav` (`VERSION`, `HUB_CONTEXT_KEY`, `SATELLITE_DOCTYPES`, …).

---

## Integração com o hub

`public/js/case_hub.js` usa os helpers `adv_case_nav_*` para:

- Cliques em linhas do painel (`data-route`)
- Pills da barra de resumo (lista filtrada e botão **+**)
- Criação de audiências, prazos, documentos, etc.

Assim, ao abrir um Case Document pela aba Documentos e voltar, o serviço reabre em **tab_documents**.

### Aba Financeiro (`tab_financial`)

KPIs e listas carregados por `case_hub.py` / `case_hub.js`:

| Elemento | Significado |
| --- | --- |
| Honorários contratados | Valor do **Fee Agreement** do serviço |
| Parcelas pendentes | Pagamentos de honorários ainda não recebidos |
| A faturar (serviços) | Itens em **Service Record** ainda não sincronizados |
| Cobranças de serviços em aberto | Cobranças com pagamento emitido e saldo pendente |

Guia operador: seção *Honorários vs Cobrança de serviços* em [manual_usuario.md](./manual_usuario.md).

---

## Adicionar novo satélite

1. Garantir campo Link `legal_case` → Legal Case no JSON do DocType.
2. Incluir o nome do DocType em `SATELLITE_DOCTYPES` (`adv_case_nav.js`).
3. Se o fieldname for diferente de `legal_case`, registrar em `CASE_FIELD_BY_DOCTYPE`.
4. No hub (`case_hub.js`), usar `adv_case_nav_follow_route` / `adv_case_nav_new_doc` na navegação.
5. Atualizar este documento e [case_documents.md](./case_documents.md) se aplicável.

---

## Comportamento sem contexto

Navegação direta (lista global, busca, link externo):

- Breadcrumb do serviço ainda aparece se `legal_case` estiver preenchido no form.
- Botão **Voltar ao Serviço** funciona normalmente.
- Restauração de aba **não** ocorre (sessionStorage vazio ou de outro serviço).

---

## Testes

Navegação é validada manualmente no browser após `bench build --app advocacia`.

Suite Python (regressão geral):

```bash
bench --site advocacia.local run-tests --app advocacia
```
