# E2E Playwright — App Advocacia

**Script:** `advocacia/advocacia/tests/e2e/playwright_flow.py`  
**Marcador:** `_PW_E2E_` (cleanup automático ao final)  
**Versão app:** 0.7.0

---

## Objetivo

Validar o fluxo completo na UI (Client → Serviço → satélites) com dados fictícios, **sem alterar documentos existentes**. Complementa a suite `run-tests` (230 testes backend), que não cobre interação browser.

---

## Requisitos

```bash
pip install playwright          # ou usar env do bench
playwright install chromium
sudo playwright install-deps    # libnspr4 etc. no Linux (obrigatório em servidores headless)
```

---

## Variáveis de ambiente

| Variável | Default | Descrição |
| --- | --- | --- |
| `ADVOCACIA_E2E_PWD` | *(obrigatória)* | Senha do usuário de teste |
| `ADVOCACIA_E2E_USER` | `Administrator` | Login |
| `ADVOCACIA_E2E_SITE` | `advocacia.local` | Site Frappe |
| `ADVOCACIA_E2E_URL` | `http://127.0.0.1:8000` | URL base |
| `ADVOCACIA_E2E_HOST` | `advocacia.local` | Header `Host` |
| `FRAPPE_BENCH_PATH` | auto-detect | Raiz do bench |
| `ADVOCACIA_E2E_REPORT` | `/tmp/advocacia_playwright_report_*.json` | Relatório JSON |

> **Segurança:** nunca commitar senha. Use env ou `.env` local (gitignored).

---

## Execução

```bash
export ADVOCACIA_E2E_PWD='sua-senha'

# Servidor SEM reloader (reloader quebra login HTTP em dev)
bench --site advocacia.local serve --port 8000 --noreload

# Em outro terminal, a partir da raiz do app:
python advocacia/advocacia/tests/e2e/playwright_flow.py
```

---

## DocTypes percorridos (ordem)

Jurisdiction, Court, Court Branch, Case Phase, Client, Legal Case, Fee Agreement, Service Record, Hearing, Deadline, Legal Task, Case Communication, Time Entry, Court Cost, Office Expense, Document Template, Document Kit.

---

## Limitações conhecidas

| Item | Nota |
| --- | --- |
| Document Template | Exige arquivo `.docx` anexo — pode falhar sem fixture |
| Document Kit | Exige child table `templates` — pode falhar sem template |
| Login Playwright puro | Script usa WSGI (`werkzeug.test.Client`) para cookies + Playwright para UI |
| `install-deps` | Sem libs do sistema, Chromium falha com `libnspr4.so` |

Validação backend alternativa (sem browser): executar fluxo via `frappe.get_doc` com o mesmo marcador `_PW_E2E_`.

---

## Relatório

Ao final, o script grava JSON em `ADVOCACIA_E2E_REPORT` com status por DocType (`ok` / `skip` / `fail`) e IDs criados para auditoria do cleanup.

---

*Script introduzido em jun/2026. Não faz parte de `bench run-tests` — execução manual ou CI opcional.*
