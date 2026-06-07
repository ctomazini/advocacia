# Seção 3 — Verificação de Usabilidade

**App:** `advocacia` · **Data:** 2026-06-02 · **Versão:** 0.7.0

---

## 3.1 Field descriptions (tooltips)

| Métrica | Valor |
|---|---:|
| Campos elegíveis (excl. Section/Column/Tab Break, HTML, Button) | 232 |
| Campos com `description` no JSON | 218 |
| Cobertura | **94%** (218/232) |
| Script de manutenção | `scripts/add_field_descriptions.py` |
| Aplicação | `bench execute advocacia.advocacia.scripts.add_field_descriptions.run` |

### DocTypes com descriptions completas (amostra)

| DocType | Campos descritos |
|---|---:|
| Acordo de Honorarios Processuais | 37 |
| Servico | 22 |
| Registro de Atos | 22 |
| Pagamento | 18 |
| Audiencia | 17 |
| Controle de Prazos | 16 |
| Cliente | 16 |
| Registro de Horas | 16 |

### Campos sem description (14 restantes)

Predominantemente: campos técnicos de sistema, flags internas de sync (`sincronizado_em`, `parcela_origem_id`) e breaks de layout em DocTypes menores. Prioridade baixa — não bloqueiam deploy.

### Campos financeiros sensíveis

O script acrescenta sufixo *"Visível apenas para Advocacia Manager."* em campos com `permlevel: 1` — alinhado a `setup/permissions.py`.

---

## 3.2 Máscaras e UX de formulário

**Arquivo:** `public/js/masks.js` — incluído globalmente via `hooks.py`.

| Máscara | Padrão | DocTypes |
|---|---|---|
| CPF | `999.999.999-99` | Cliente |
| CNPJ | `99.999.999/9999-99` | Cliente, Configuracao do Escritorio |
| CNJ | `9999999-99.9999.9.99.9999` | Servico |
| Celular | `(99) 99999-9999` | Contato Cliente |
| Fixo | `(99) 9999-9999` | Contato Cliente |
| CEP | `99999-999` | Endereco Cliente |

**Regra:** JS só UX — validação real em `validators.py` no `validate()` do DocType.

**Fallback:** se `jquery.inputmask` disponível (Frappe), usa inputmask nativo; senão `_bindInput` custom.

### Outros JS globais

| Arquivo | Função |
|---|---|
| `list_nav.js` | Navegação painel → lista com filtros |
| `cliente_from_servico.js` | Preenche cliente ao selecionar serviço |
| `timer_global.js` | Timer de Registro de Horas no desk |

---

## 3.3 Workspace e sidebar

### Workspace `Advocacia`

- Fixture exportada em `fixtures/workspace.json`
- Sincronizada em `after_migrate` → `setup/workspace.ensure_advocacia_workspace`
- Cards e links alinhados ao fluxo operacional do escritório

### Sidebar (`setup/sidebar.py`)

| Seção | collapsible | Links |
|---|---|---|
| Dia a Dia | 1 | Painel, Prazos, Audiências, Tarefas, Comunicações |
| Gestão de Casos | 1 | Serviços, Clientes, Horas, Atos, Custas |
| Financeiro | 1 | Pagamentos, Honorários, Despesas, Documentos, Kits |
| Relatórios | 1 (keep_closed) | 6 Script Reports |
| Cadastros | 1 (keep_closed) | Comarca, Vara, Tribunal, Fase, Escritório |

**Fix Frappe v16:** Section Breaks com filhos exigem `collapsible: 1` — sem isso o scroll do desk trava.

**Total links sidebar:** 26 entradas canônicas em `SIDEBAR_LINK_ORDER`.

---

## 3.4 List views

12 arquivos `*_list.js` em transacionais principais:

| DocType | hide_name_column | Indicador status | Filtros rápidos |
|---|---|---|---|
| Servico | ✅ title | via status | 🟡 |
| Cliente | ✅ nome + badge ID | 🟡 | — |
| Pagamento | ✅ | ✅ cores + Origem | ✅ onload |
| Acordo de Honorarios Processuais | ✅ | ✅ | 🟡 |
| Registro de Atos | ✅ | ✅ | 🟡 |
| Audiencia | ✅ | ✅ | 🟡 |
| Controle de Prazos | ✅ | ✅ | 🟡 |
| Despesa do Escritorio | ✅ | ✅ | 🟡 |
| Custa Processual | ✅ | ✅ | 🟡 |
| Comunicacao | ✅ | 🟡 | 🟡 |
| Tarefa | ✅ | ✅ | 🟡 |
| Registro de Horas | ✅ | 🟡 | — |

**Gap:** cadastros auxiliares (Comarca, Vara, Tribunal) sem `*_list.js` custom — aceitável (poucos registros).

---

## 3.5 Títulos visíveis

| Padrão | Exemplo |
|---|---|
| Transacionais | `SERV-2026-0042 — Silva Advogados Ltda` |
| Cliente | `CLI-2026-0015 — João da Silva` (title_field = nome) |
| Cadastros | Nome do campo autoname |

`show_title_field_in_link: 1` nos transacionais — links e painel exibem descritor legível.

---

## 3.6 Fluxos operacionais

### Fluxo 1: Novo processo judicial

1. **Cliente** — CPF/CNPJ validado ✅  
2. **Comarca / Vara / Tribunal** — cadastro rígido ✅  
3. **Servico** — tipo Processo Judicial + CNJ ✅  
4. **Acordo de Honorarios** — parcelas + sync Pagamento ✅  
5. **Painel** — KPIs e timeline ✅  

**Fricção:** 🟡 Orçamento de honorários complexo (modos Misto/Percentual) — descriptions ajudam.

### Fluxo 2: Prazo processual

1. **Controle de Prazos** — datas cronológicas validadas ✅  
2. **Event** — sync automático ✅  
3. **Notificação** — scheduler diário ✅  

### Fluxo 3: Cobrança de atos

1. **Registro de Atos** — tabela Ato Advocaticio ✅  
2. **Gerar pagamento** — whitelist sync ✅  
3. **Pagamento** — coluna Origem na list view ✅  

---

## 3.7 Demo data (dev)

| Comando | Função |
|---|---|
| `bench seed-demo --site advocacia.local` | Popula dados com `_DEMO_` |
| `bench clear-demo --site advocacia.local` | Remove por marcador |

**Produção:** não executar — módulo marcado dev-only.

---

## 3.8 Gaps de usabilidade

| Gap | Severidade | Ação sugerida |
|---|---|---|
| 14 campos sem description | 🟢 | Completar no próximo sprint UX |
| Tarefa/Pagamento fora Connections do Servico | 🟢 | Adicionar DocType Links |
| Onboarding in-app | 🟡 | Workspace intro ou vídeo |
| Mobile desk | 🟡 | Painel responsivo parcial (CSS vars) |

---

## 3.9 Checklist UX pré-release

- [ ] `bench build --app advocacia` após JS
- [ ] Smoke: máscara CNJ em Servico novo
- [ ] Smoke: tooltip em Acordo (campo honorários)
- [ ] Smoke: sidebar colapsa sem travar scroll
- [ ] Smoke: lista Pagamento mostra coluna Origem
- [ ] User sem valores financeiros no painel

---

*Usabilidade v0.7.0: descriptions 94%, painel modular, sidebar v16-safe.*
