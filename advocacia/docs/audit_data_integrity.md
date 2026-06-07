# Seção 5 — Integridade de Dados e Validações

**App:** `advocacia` · **Módulo:** `validators.py` · **Data:** 2026-06-02 · **Versão:** 0.7.0

---

## 5.1 Validadores regulatórios brasileiros

Arquivo central: `advocacia/advocacia/validators.py` (193 linhas).  
Testes dedicados: `test_validators.py` (16 métodos).

### CPF (`validar_cpf`)

| Regra | Implementação |
|---|---|
| Armazenamento | Apenas dígitos (`limpar_numerico`) |
| Tamanho | 11 dígitos |
| Sequências repetidas | Rejeita (`11111111111`, etc.) |
| Dígitos verificadores | Algoritmo Receita Federal (módulo 11) |
| Campo vazio | Permite (validação condicional no controller) |

**Usado em:** `Cliente` (cpf, cpf_representante), factories de teste, `seed_demo.py` (`_demo_cpf`).

### CNPJ (`validar_cnpj`)

| Regra | Implementação |
|---|---|
| Armazenamento | Apenas dígitos |
| Tamanho | 14 dígitos |
| Sequências repetidas | Rejeita |
| Dígitos verificadores | Pesos Receita Federal |
| Campo vazio | Permite |

**Usado em:** `Cliente`, `Configuracao do Escritorio`, `seed_demo.py` (`_demo_cnpj`).

### CNJ (`validar_cnj`)

| Regra | Implementação |
|---|---|
| Formato | 20 dígitos (Resolução CNJ 65/2008) |
| DV | Módulo 97 Base 10 (`_calcular_dv_cnj`) |
| Ano do processo | Entre 1900 e ano corrente |
| Máscara UI | `9999999-99.9999.9.99.9999` (`masks.js`) |

**Usado em:** `Servico.numero_processo` (obrigatório para tipo Processo Judicial).

### Telefone (`validar_telefone`)

| Tipo | Regras |
|---|---|
| DDD | Lista `DDDS_VALIDOS` (ANATEL — 67 DDDs geográficos) |
| Celular | 11 dígitos; nono dígito = 9; segundo dígito local ≠ 0/1 |
| Fixo | 10 dígitos; primeiro dígito local entre 2 e 5 |

**Usado em:** `Contato Cliente` (telefone, celular), child tables de Cliente.

### E-mail (`validar_email`)

| Regra | Implementação |
|---|---|
| Normalização | `.strip().lower()` antes de salvar |
| Formato | Rejeita se sem `@` ou domínio sem `.` |

**Usado em:** `Contato Cliente`, `Cliente` (contatos).

---

## 5.2 Onde as validações são aplicadas

| DocType | Campo | Validador | Momento |
|---|---|---|---|
| Cliente | cpf | `validar_cpf` | `validate()` |
| Cliente | cnpj | `validar_cnpj` | `validate()` |
| Cliente | cpf_representante | `validar_cpf` | `validate()` |
| Contato Cliente | telefone, celular | `validar_telefone` | `validate()` |
| Contato Cliente | email | `validar_email` | `validate()` |
| Servico | numero_processo | `validar_cnj` | `validate()` (se Processo Judicial) |
| Configuracao do Escritorio | cnpj_escritorio | `validar_cnpj` | `validate()` |

**Princípio:** validação pesada no `.py` do DocType com `frappe.throw()` — JS (`masks.js`) é apenas UX.

---

## 5.3 Regras de cronologia e negócio

| Regra | DocType | Status |
|---|---|---|
| Data Fato ≤ Distribuição ≤ Intimação < Prazo Fatal | Controle de Prazos | ✅ `validate()` |
| CNJ obrigatório se Processo Judicial | Servico | ✅ |
| Comarca/Vara/Tribunal/Fase — Link rígido | Servico, cadastros | ✅ |
| CPF ou CNPJ conforme tipo_pessoa | Cliente | ✅ |
| Endereço principal único | Cliente (child) | ✅ controller |
| Valores negativos bloqueados | Pagamento, Acordo, Custa | ✅ |
| Overpayment parcela | Pagamento | ✅ |

---

## 5.4 Sync financeiro (integridade transacional)

### Acordo de Honorarios → Pagamento

| Aspecto | Status |
|---|---|
| `parcela_origem_id` estável por linha child | ✅ |
| Sync idempotente `on_update` acordo | ✅ `financeiro.sincronizar_pagamentos_hook` |
| Flag reentrância `frappe.flags.in_pagamento_sync` | ✅ |
| `manual_override` preserva edição manual | ✅ |
| Cancelamento órfãos | ✅ |
| Testes | ✅ `test_financeiro.py`, `test_acordo_honorarios.py` |

### Registro de Atos → Pagamento

| Aspecto | Status |
|---|---|
| Upsert idempotente por registro | ✅ `sincronizar_pagamento_atos` |
| Tipo origem `Atos Advocatícios` | ✅ |
| Testes | ✅ `test_registro_atos.py` |

**Proibido:** `frappe.db.commit()` em hooks de sync — Frappe commita o request.

---

## 5.5 Títulos compostos (`titulos.py`)

| Função | Quando |
|---|---|
| `recompor_titulo_se_vazio` | `validate()` |
| `aplicar_titulo_pos_insert` | `after_insert()` |
| `backfill_titulos_vazios` | Setup manual (com `commit`) |

Formato: `{name} — {descritor}` com separador `" — "`.

**Testes:** `test_titulos.py` (10 métodos).

---

## 5.6 Cobertura de testes de integridade

| Área | Testes | Status |
|---|---|---|
| CPF válido/inválido/DV | test_validators | 🟢 |
| CNPJ válido/inválido/DV | test_validators | 🟢 |
| CNJ DV módulo 97 | test_validators, test_servico | 🟢 |
| Telefone DDD/celular/fixo | test_validators | 🟢 |
| E-mail lower | test_validators | 🟢 |
| Sync pagamentos acordo | test_financeiro | 🟢 |
| Sync atos | test_registro_atos | 🟢 |
| Cronologia prazos | test_controle_prazos | 🟢 |

---

## 5.7 Gaps e recomendações

| Gap | Severidade | Ação |
|---|---|---|
| OAB do advogado | 🟡 | Não validado (campo futuro) |
| CEP via ViaCEP | 🟢 | Apenas dígitos + máscara; sem validação checksum |
| CPF/CNPJ duplicado entre clientes | 🟡 | `unique` não forçado globalmente — decisão de negócio |
| Rollup valor_causa → honorários % | 🟢 | Calculado no Acordo, não rollup automático |

---

*Validações são a primeira linha de defesa; máscaras JS não substituem `validators.py`.*
