# Documentos do processo

Dois fluxos distintos convivem no app:

| Fluxo | DocType | Saída |
| --- | --- | --- |
| **Geração Word** | Document Template + Document Kit | `.docx` preenchido via docxtpl |
| **Repositório de arquivos** | Case Document | PDF, petições, procurações e anexos do processo |

Referência cruzada: [manual_usuario.md](./manual_usuario.md) (operador) · [hub_navigation.md](./hub_navigation.md) (navegação).

---

## Document Category

Cadastro rígido (`category_name` único). Seed idempotente em `setup/seed.py` (`ensure_seed_data`):

Petição, Procuração, Certidão, Decisão, Contrato, Acordo, Substabelecimento, Comprovante, Protocolo, Laudo, Outro.

Sidebar: **Cadastros → Categorias de Documento**.

---

## Case Document

Satélite de **Legal Case** (`legal_case`).

| Campo | Descrição |
| --- | --- |
| `legal_case` | Link → Legal Case (obrigatório) |
| `client` | Fetch de `legal_case.client` (read-only) |
| `category` | Link → Document Category |
| `status` | Rascunho, Assinado, Protocolado, Juntado, Substituído |
| `source` | Gerado pelo App, Upload Manual, Digitalizado |
| `title` | Composição automática (read-only na prática) |
| `version_label` | Versão / revisão (ex.: v1, Rev_01) |
| `file` | Anexo (obrigatório) |
| `related_deadline` | Link opcional → Deadline (mesmo serviço) |
| `remarks` | Observações |

**ID:** `DOC-{YYYY}-{####}`

### Título (`case_document_naming.py`)

`{Categoria} — {Título do serviço}[ — {Versão}]`

Exemplo: `Petição — SERV-2026-0042 — Cliente Exemplo — v1`

### Validações (`case_document.py`)

- `validate()`: sincroniza cliente, compõe título, valida prazo
- `related_deadline` deve pertencer ao mesmo `legal_case`

---

## Fluxo de geração automática

Arquivo: `advocacia/advocacia/documentos.py`

```
gerar_documentos_em_lote(servico_name, templates)
  → _build_context(servico_name)
  → _render_and_attach()          # docxtpl → File anexado ao Legal Case
  → _create_generated_case_document()
       category = _ensure_document_category(_infer_category(template_doc))
       source = "Gerado pelo App"
       status = "Rascunho"
       version_label = "v1"
```

Whitelisted: `gerar_documentos_em_lote`, `get_templates_disponiveis`, `get_kits_disponiveis`, `get_placeholders_referencia`.

Resposta de lote inclui `case_document` (name) em cada item de `gerados`.

---

## Mapa de categorias inferidas

Função `_infer_category(template_doc)` analisa `title`, `document_type` e `description` do **Document Template** (case-insensitive).

### Palavras-chave (`TEMPLATE_CATEGORY_MAP`)

| Palavra-chave (trecho) | Categoria |
| --- | --- |
| procuracao, procuração, mandato | Procuração |
| contrato, honorario, honorários | Contrato |
| acordo | Acordo |
| peticao, petição, inicial, contestação, recurso | Petição |
| substabelecimento | Substabelecimento |
| declaracao, declaração | Outro |
| certidao, certidão | Certidão |
| decisao, decisão, sentença | Decisão |
| comprovante, recibo | Comprovante |
| protocolo, requerimento | Protocolo |
| laudo | Laudo |

### Fallback por `document_type` do template

| document_type | Categoria |
| --- | --- |
| Contrato | Contrato |
| Declaracao | Outro |
| Recibo | Comprovante |
| Carta | Outro |
| Ficha de Atendimento | Outro |
| Outro | Outro |

Se nenhuma regra casar → **Outro**. Categorias inexistentes são criadas via `_ensure_document_category` (setup filho).

---

## Hub — aba Documentos

Backend: `case_hub.py` → `get_case_documents()`, contagem em `get_case_counts()`.

Frontend: `public/js/case_hub.js` → painel `documents_panel` no Legal Case.

- Pill **Documentos** na barra de resumo
- Botões **+ Enviar** e **Gerar .docx**
- Lista com status, categoria, link do arquivo

---

## Placeholders (.docx)

Fonte de verdade: `PLACEHOLDER_REFERENCIA` em `documentos.py`.

Grupos: Escritório, Cliente, Endereço, Contato, Serviço/processo, Honorários (condicional), Parcela do acordo (loop), Data, Legados.

Campos novos relevantes:

| Placeholder | Uso |
| --- | --- |
| `cliente_data_nascimento` | Data de nascimento do cliente PF |
| `cliente_rg_emissor` | Órgão emissor do RG |
| `escritorio_advogada_cpf` | CPF da advogada principal (mascarado) |
| `escritorio_advogada_rg` | RG da advogada principal |
| `acordo_valor_extenso` | Valor total contratado por extenso |
| `acordo_narrativa_pagamento` | Texto agrupado das parcelas (honorários) |
| `acordo_parcelas` | Lista para loop Jinja |

Exemplo de loop de parcelas:

```jinja
{% for p in acordo_parcelas %}
{{ p.description }} — {{ p.lawyer_amount_fmt }} — venc. {{ p.due_date_fmt }}
{% endfor %}
```

UI: botão **Ver Placeholders Disponíveis** no Document Template · módulo `documentos_placeholders.js`.

Regenerar tabelas no manual: `bench execute advocacia.advocacia.scripts.generate_manual.main`

---

## Testes

| Arquivo | Cobertura |
| --- | --- |
| `doctype/case_document/test_case_document.py` | CRUD, título, prazo |
| `doctype/document_category/test_document_category.py` | Cadastro |
| `tests/test_case_hub.py` | Lista e contagem no hub |
| `tests/test_documentos.py` | Geração + inferência de categoria |

```bash
bench --site advocacia.local run-tests --app advocacia
```

---


---

**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** 1.1.0
