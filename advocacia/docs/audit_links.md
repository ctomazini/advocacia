# Seção 2 — Cross-check de Links entre DocTypes

**App:** `advocacia` · **Hub:** `Servico` · **Data:** 2026-06-02 · **Versão:** 0.7.0

---

## 2.1 Mapa de relacionamentos

```
Cliente
  ├── contatos (Table → Contato Cliente)
  ├── enderecos (Table → Endereco Cliente)
  └── Linkado POR:
      ├── Servico.cliente
      ├── Acordo de Honorarios Processuais.cliente (fetch)
      └── (fetch_from indireto via servico em satélites)

Servico  [HUB]
  ├── cliente (Link → Cliente)
  ├── comarca, vara, tribunal, fase_processual (Link → cadastros rígidos)
  └── Linkado POR (satélites com campo servico):
      ├── Acordo de Honorarios Processuais.servico
      ├── Registro de Atos.servico
      ├── Audiencia.servico
      ├── Controle de Prazos.servico
      ├── Custa Processual.servico
      ├── Comunicacao.servico
      ├── Registro de Horas.servico
      ├── Tarefa.servico
      └── Pagamento.servico (derivado de acordo/atos)

Acordo de Honorarios Processuais
  ├── servico, cliente (Link)
  ├── parcelas (Table → Parcela de Honorarios)
  │     └── sync → Pagamento (parcela_origem_id)
  └── Linkado POR: Pagamento.acordo

Registro de Atos
  ├── servico, cliente (Link)
  ├── atos (Table → Ato Advocaticio)
  └── sync → Pagamento (tipo_origem Atos)

Pagamento
  ├── servico, cliente, acordo, registro_atos (Link)
  └── Camada financeira única (honorários + atos)

Kit de Documentos
  ├── itens (Table → Kit Documento Item → Template Documento)
  └── Sem link direto a Servico (uso via gerador documentos)
```

---

## 2.2 Satélites do hub Servico (9)

| DocType | Campo | fetch cliente | Dashboard link no Servico |
|---|---|---|---|
| Acordo de Honorarios Processuais | servico | ✅ | Honorários |
| Registro de Atos | servico | ✅ | Atos |
| Audiencia | servico | ✅ | Agenda |
| Controle de Prazos | servico | ✅ | Agenda |
| Custa Processual | servico | ✅ | Financeiro |
| Comunicacao | servico | ✅ | Comunicação |
| Registro de Horas | servico | ✅ | Produtividade |
| Tarefa | servico | ✅ | — (sem DocType Link no JSON) |
| Pagamento | servico | ✅ | — (via acordo/atos) |

**Padrão hub-and-spoke:** satélite carrega `servico` (Link) + `cliente` (Link ou `fetch_from` servico).

Exemplo no Acordo:
```python
if not self.cliente and self.servico:
    self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
```

---

## 2.3 Cadastros rígidos (nunca texto livre)

| Conceito | DocType | autoname | Usado em |
|---|---|---|---|
| Comarca | Comarca | field:comarca_name | Servico, Vara |
| Vara | Vara | field:vara_name | Servico |
| Tribunal | Tribunal | field:tribunal_name | Servico |
| Fase processual | Fase Processual | field:phase_name | Servico |

**Proibido:** `Data`/`Small Text` para estes conceitos repetitivos.

---

## 2.4 Child tables (5)

| Parent | Child | Relação |
|---|---|---|
| Cliente | Contato Cliente | contatos |
| Cliente | Endereco Cliente | enderecos |
| Acordo de Honorarios Processuais | Parcela de Honorarios | parcelas |
| Registro de Atos | Ato Advocaticio | atos |
| Kit de Documentos | Kit Documento Item | itens |

Child tables **não** têm `title_field` próprio — herdam contexto do pai.

---

## 2.5 DocType Links no formulário Servico

Configurados em `servico.json` → aba Connections:

| Grupo | DocType linkado | link_fieldname |
|---|---|---|
| Honorários | Acordo de Honorarios Processuais | servico |
| Atos | Registro de Atos | servico |
| Agenda | Audiencia | servico |
| Agenda | Controle de Prazos | servico |
| Financeiro | Custa Processual | servico |
| Comunicação | Comunicacao | servico |
| Produtividade | Registro de Horas | servico |

**Gap menor:** `Tarefa` e `Pagamento` têm `servico` mas não aparecem na aba Connections do Servico — acessíveis via lista filtrada ou painel.

---

## 2.6 Integridade referencial

| Verificação | Status |
|---|---|
| Servico exige Cliente | ✅ reqd |
| Satélite sem servico órfão em produção | 🟡 depende de uso |
| Delete Servico com filhos | 🟡 Frappe impede se houver link — sem cascade custom |
| Pagamento órfão após delete acordo | ✅ sync cancela órfãos |
| standard_queries Servico | ✅ `servico_query` em hooks |

---

## 2.7 Queries e navegação

| Recurso | Uso |
|---|---|
| `standard_queries["Servico"]` | Autocomplete filtrado |
| `list_nav.js` | Painel e Connections → lista com filtros `{servico: X}` etc. |
| `list_filters.js` | Filtros padrão responsivos em todas as list views |
| `cliente_from_servico.js` | Preenche cliente ao escolher serviço |
| Reports (6) | Agrupam por servico/cliente |

---

## 2.8 Comparação com engenharia

| | Advocacia | Engenharia |
|---|---|---|
| Hub | Servico | Construction Project |
| Satélites com hub link | 9 | 12+ |
| Domínio | Jurídico BR | Obra/civil |
| Naming | PT congelado | EN greenfield |

**Não renomear** `Servico` → `Service` — brownfield com dados e fixtures.

---

## 2.9 Checklist novo satélite

Ao criar DocType que orbita um processo:

- [ ] Campo `servico` (Link → Servico, reqd)
- [ ] Campo `cliente` com `fetch_from` ou populate em `validate()`
- [ ] `title_field` + `titulos.py` se transacional
- [ ] DocType Link no `servico.json` (opcional mas recomendado)
- [ ] Teste CRUD com `create_test_servico()`
- [ ] Entrada na sidebar/workspace se operacional

---

*Mapa estável desde v0.7.0. Alterações de hub exigem migration plan e patch de dados.*
