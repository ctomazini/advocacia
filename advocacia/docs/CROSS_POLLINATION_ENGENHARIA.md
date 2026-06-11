# Cross-pollination: Engenharia → Advocacia

**Objetivo:** alinhar funcionalidades do app **engenharia** (referência implementada) no app **advocacia** (brownfield migrado v1.0.0), **sem** copiar nomes EN de DocType do engenharia literalmente onde o domínio jurídico exige nome PT de label ou conceito distinto.

**Nomenclatura advocacia (norma vigente):**

| Camada | Idioma |
| --- | --- |
| DocType `name` | Inglês Title Case (`Legal Case`, …) |
| `fieldname` | Inglês snake_case (majoritário) |
| Labels / `_()` / manual | Português |

**Hub advocacia:** `Legal Case` (equivalente a `Construction Project`).

---

## Prompt operacional (colar no Agent)

```
Contexto:
- Repositório advocacia: /home/frappe/frappe-bench/apps/advocacia
- Repositório engenharia (somente leitura): /home/frappe/frappe-bench/apps/engenharia
- NUNCA modificar arquivos em apps/engenharia/
- Seguir REGRAS_ADVOCACIA.md e Conventional Commits
- Um DocType novo ou alteração estrutural relevante por commit (quando aplicável)

Objetivo:
Portar para advocacia os padrões do engenharia listados abaixo, adaptando domínio jurídico (Legal Case, Client, Fee Agreement, Permit/Deadline, etc.).

Blocos (prioridade):
1) Repositório de arquivos do processo (equivalente Project Document + Document Category)
2) Hub: aba/painel Documentos + API case_hub
3) Geração Word: pós-geração registrando metadados + placeholders faltantes (parcelas acordo, protocolo expandido)
4) Navegação hub (equivalente eng_hub_nav.js) — breadcrumb, voltar ao serviço, restaurar aba
5) Documentação: manual_usuario.md + guias em advocacia/docs/

Referências engenharia (ler antes de codar):
- engenharia/project_document_naming.py
- engenharia/documents.py (geração + placeholders)
- engenharia/public/js/eng_hub_nav.js
- engenharia/public/js/hub.js + project_hub.py
- engenharia/docs/project_documents.md, hub_navigation.md

Referências advocacia (estender):
- advocacia/advocacia/documentos.py
- advocacia/advocacia/case_hub.py + public/js/case_hub.js
- advocacia/advocacia/doctype/legal_case/

De-para conceitual (NÃO copiar nomes EN de DocType do engenharia):
| Engenharia | Advocacia |
| Construction Project | Legal Case |
| Project Document | Documento do Processo (nome a confirmar) |
| Document Category | Categoria de Documento |
| eng_hub_nav | adv_case_nav (novo JS global) |
| eng-dashboard | painel (Page) |

Definition of Done por bloco:
- bench --site advocacia.local migrate (se patch)
- bench build --app advocacia && clear-cache
- bench --site advocacia.local run-tests --app advocacia verde
- Atualizar manual_usuario.md / advocacia/docs/ no mesmo PR quando UX mudar

Proibido:
- Renomear DocTypes existentes sem patch
- frappe.db.commit() fora de setup/patches
- Alterar apps/engenharia/
```

---

## Mapa de port (detalhe)

### 1. Documento do processo + categoria

| Engenharia | Advocacia (proposto) |
| --- | --- |
| `Document Category` | `Document Category` ou `Case Document Category` |
| `Project Document` | `Case Document` / `Legal Case Document` |
| `project_document_naming.py` | `case_document_naming.py` (adaptar prefixos `DOC-` ou `ANEX-`) |
| Patch categoria Link | Patch idempotente se houver legado |
| Hub aba Documentos | Aba/painel em `case_hub.js` |

**Campos sugeridos:** `legal_case`, `client`, `category` (Link), `version_label`, `title_descriptor`, `title` (composto), `status`, `source`, `file`, `related_permit` (opcional).

### 2. Geração Word (`documentos.py`)

- Portar grupos/lógica novos: parcelas de acordo, protocolo expandido, totais — onde aplicável.
- Manter placeholders **PT** (`cliente_nome`, `servico_codigo`, …).
- UI `documents_placeholders.js`: `escritorio_logo`, badges condicionais.
- Opcional: ao gerar, criar `Case Document` + inferir categoria do template.

### 3. Hub + navegação

- Estender `get_case_hub_data` com contagem/lista de documentos.
- Novo `adv_case_nav.js` (espelho `eng_hub_nav.js`): breadcrumb, «Voltar ao serviço», `sessionStorage` para aba.
- Lista fechada de satélites com link `legal_case`.

### 4. O que NÃO portar sem demanda

- Project Item / orçamento técnico (obra)
- Building Type, Work Cost, Subcontract domínio obra
- DocTypes engenharia-only sem equivalente jurídico

---

## Sequência sugerida de commits

1. `feat: add Document Category for case files`
2. `feat: add Case Document with naming and file rename`
3. `feat: extend case hub with documents panel`
4. `feat: link document generation to case document records`
5. `feat: add adv case hub navigation and breadcrumbs`
6. `feat: expand document placeholders for fee agreement and permits`
7. `docs: update manual and cross-pollination guides`

---

## Verificação final

```bash
cd /home/frappe/frappe-bench
bench --site advocacia.local migrate
bench build --app advocacia
bench --site advocacia.local clear-cache
bench --site advocacia.local run-tests --app advocacia
```

---

## Documentação a atualizar (advocacia)

- `advocacia/docs/manual_usuario.md` — § documentos + § navegação hub
- `advocacia/docs/case_documents.md` (criar após implementar)
- `advocacia/docs/hub_navigation.md` (criar após implementar)
- `docs/crosscheck_engenharia.md` (engenharia) — já reflete v1.0.0 EN

---

*Gerado para alinhar advocacia ao engenharia. Executar o prompt acima em sessões Agent dedicadas por bloco.*
