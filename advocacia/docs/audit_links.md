# Seção 2 — Cross-check de Links entre DocTypes

**App:** `advocacia` · **Hub:** `Legal Case` · **Data:** 2026-06-23 · **Versão:** 1.1.0

---

## 2.1 Mapa de relacionamentos

```
Client
  ├── contatos (Table → Client Contact)
  ├── enderecos (Table → Client Address)
  └── Linkado POR:
      ├── Legal Case.cliente
      ├── Fee Agreement.cliente (fetch)
      └── (fetch_from indireto via servico em satélites)

Legal Case  [HUB]
  ├── cliente (Link → Client)
  ├── comarca, vara, tribunal, fase_processual (Link → cadastros rígidos)
  └── Linkado POR (satélites com campo servico):
      ├── Fee Agreement.servico
      ├── Service Record.servico
      ├── Hearing.servico
      ├── Deadline.servico
      ├── Court Cost.servico
      ├── Case Communication.servico
      ├── Time Entry.servico
      ├── Legal Task.servico
      └── Legal Payment.servico (derivado de acordo/atos)

Fee Agreement
  ├── servico, cliente (Link)
  ├── parcelas (Table → Fee Installment)
  │     └── sync → Legal Payment (parcela_origem_id)
  └── Linkado POR: Legal Payment.acordo

Service Record
  ├── servico, cliente (Link)
  ├── atos (Table → Legal Act Item)
  └── sync → Legal Payment (tipo_origem Atos)

Legal Payment
  ├── servico, cliente, acordo, registro_atos (Link)
  └── Camada financeira única (honorários + atos)

Document Kit
  ├── itens (Table → Document Kit Item → Document Template)
  └── Sem link direto a Legal Case (uso via gerador documentos)
```

---

## 2.2 Satélites do hub Legal Case (9)

| DocType | Campo | fetch cliente | Dashboard link no Legal Case |
|---|---|---|---|
| Fee Agreement | servico | ✅ | Honorários |
| Service Record | servico | ✅ | Atos |
| Hearing | servico | ✅ | Agenda |
| Deadline | servico | ✅ | Agenda |
| Court Cost | servico | ✅ | Financeiro |
| Case Communication | servico | ✅ | Comunicação |
| Time Entry | servico | ✅ | Produtividade |
| Legal Task | servico | ✅ | — (sem DocType Link no JSON) |
| Legal Payment | servico | ✅ | — (via acordo/atos) |

**Padrão hub-and-spoke:** satélite carrega `servico` (Link) + `cliente` (Link ou `fetch_from` servico).

Exemplo no Acordo:
```python
if not self.cliente and self.servico:
    self.cliente = frappe.db.get_value("Legal Case", self.servico, "cliente")
```

---

## 2.3 Cadastros rígidos (nunca texto livre)

| Conceito | DocType | autoname | Usado em |
|---|---|---|---|
| Jurisdiction | Jurisdiction | field:jurisdiction_name | Legal Case, Court Branch |
| Court Branch | Court Branch | field:court_branch_name | Legal Case |
| Court | Court | field:court_name | Legal Case |
| Fase processual | Case Phase | field:case_phase_name | Legal Case |

**Proibido:** `Data`/`Small Text` para estes conceitos repetitivos.

---

## 2.4 Child tables (5)

| Parent | Child | Relação |
|---|---|---|
| Client | Client Contact | contatos |
| Client | Client Address | enderecos |
| Fee Agreement | Fee Installment | parcelas |
| Service Record | Legal Act Item | atos |
| Document Kit | Document Kit Item | itens |

Child tables **não** têm `title_field` próprio — herdam contexto do pai.

---

## 2.5 DocType Links no formulário Legal Case

Configurados em `servico.json` → aba Connections:

| Grupo | DocType linkado | link_fieldname |
|---|---|---|
| Honorários | Fee Agreement | servico |
| Atos | Service Record | servico |
| Agenda | Hearing | servico |
| Agenda | Deadline | servico |
| Financeiro | Court Cost | servico |
| Comunicação | Case Communication | servico |
| Produtividade | Time Entry | servico |

**Gap menor:** `Legal Task` e `Legal Payment` têm `servico` mas não aparecem na aba Connections do Legal Case — acessíveis via lista filtrada ou painel.

---

## 2.6 Integridade referencial

| Verificação | Status |
|---|---|
| Legal Case exige Client | ✅ reqd |
| Satélite sem servico órfão em produção | 🟡 depende de uso |
| Delete Legal Case com filhos | 🟡 Frappe impede se houver link — sem cascade custom |
| Legal Payment órfão após delete acordo | ✅ sync cancela órfãos |
| standard_queries Legal Case | ✅ `servico_query` em hooks |

---

## 2.7 Queries e navegação

| Recurso | Uso |
|---|---|
| `standard_queries["Legal Case"]` | Autocomplete filtrado |
| `list_nav.js` | Painel e Connections → lista com filtros `{servico: X}` etc. |
| `list_filters.js` | Filtros padrão responsivos em todas as list views |
| `cliente_from_servico.js` | Preenche cliente ao escolher serviço |
| Reports (6) | Agrupam por servico/cliente |

---

## 2.8 Comparação com engenharia

| | Advocacia | Engenharia |
|---|---|---|
| Hub | Legal Case | Construction Project |
| Satélites com hub link | 9 | 12+ |
| Domínio | Jurídico BR | Obra/civil |
| Naming | PT congelado | EN greenfield |

**Não renomear** `Legal Case` → `Service` — brownfield com dados e fixtures.

---

## 2.9 Checklist novo satélite

Ao criar DocType que orbita um processo:

- [ ] Campo `servico` (Link → Legal Case, reqd)
- [ ] Campo `cliente` com `fetch_from` ou populate em `validate()`
- [ ] `title_field` + `titulos.py` se transacional
- [ ] DocType Link no `servico.json` (opcional mas recomendado)
- [ ] Teste CRUD com `create_test_legal_case()`
- [ ] Entrada na sidebar/workspace se operacional

---

*Mapa estável desde v0.7.0. Alterações de hub exigem migration plan e patch de dados.*

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
