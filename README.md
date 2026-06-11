# Advocacia

Aplicativo Frappe v16 para gestão jurídica de escritórios de advocacia no Brasil: clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, documentos do processo, despesas operacionais, painel operacional, geração de documentos (.docx) e API read-only para agentes IA.

**Versão:** 1.0.0 · **Branch:** `main`

Documentação: [advocacia/docs/README.md](./advocacia/docs/README.md) (índice) · [CODEBASE.md](./CODEBASE.md) · [REGRAS_ADVOCACIA.md](./REGRAS_ADVOCACIA.md) · [Layout forms](./advocacia/docs/audit_form_layout.md) · [Manual](./advocacia/docs/manual_usuario.md)

## Requisitos

- [Frappe Bench](https://github.com/frappe/bench) com Frappe v16.x
- Python 3.12+
- Node.js **20+** (Frappe v16.19 recomenda **Node ≥24** para `bench build`)
- MariaDB 10.6+
- Dependência Python: `docxtpl>=0.18.0` (instalada via `pyproject.toml`)

## Instalação

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/ctomazini/advocacia.git --branch main
bench --site seu-site.local install-app advocacia
bench --site seu-site.local migrate
bench build --app advocacia
bench restart
```

## Testes

```bash
bench --site seu-site.local set-config allow_tests true
bench --site seu-site.local run-tests --app advocacia
```

Suíte atual: **297 testes** (`bench run-tests --app advocacia`, jun/2026).

## DocTypes do app

Cadastros: Client, Jurisdiction, Court Branch, Court, Case Phase, Document Category · Hub: Legal Case · Processual: Hearing, Deadline, Legal Task, Case Communication · Financeiro: Fee Agreement, Legal Payment, Court Cost, Office Expense · Atividades: Service Record, Time Entry · Documentos: Case Document, Document Template, Document Kit · Config: Office Settings · Tabelas filhas: Client Contact, Client Address, Fee Installment, Legal Act Item, Document Kit Item.

E2E browser (opcional): [advocacia/docs/e2e_playwright.md](./advocacia/docs/e2e_playwright.md)

## Dados de demonstração (dev)

```bash
bench --site seu-site.local seed-demo-advocacia   # popula ~130 registros demo
bench --site seu-site.local clear-demo-advocacia  # remove todos com _DEMO_
```

> Se o app **engenharia** estiver instalado no bench, use `seed-demo-advocacia` (o comando genérico `seed-demo` aponta para engenharia).

## Google Calendar (sincronização de agenda)

Audiências e Prazos criados no app geram **Events** nativos do Frappe, que podem sincronizar com Google Calendar via integração padrão do Frappe:

1. **Google Cloud Console** → criar projeto → habilitar **Calendar API**
2. **Credenciais** → OAuth 2.0 → Redirect URI:  
   `https://{seu-site}/api/method/frappe.integrations.doctype.google_calendar.google_calendar.google_callback`
3. No Frappe: **Google Settings** → Client ID + Client Secret
4. Criar registro em **Google Calendar** → autorizar conta Gmail
5. Events criados automaticamente pelos hooks `calendar_sync.py` sincronizam com o calendário autorizado

## Desenvolvimento

Após alterar DocType JSON: `bench --site seu-site.local migrate`  
Após alterar JS de DocType: `bench --site seu-site.local clear-cache`  
Após alterar `public/js/` ou `public/css/`: `bench build --app advocacia`

Regenerar documentação:

```bash
python scripts/generate_codebase.py
bench --site seu-site.local execute advocacia.advocacia.scripts.generate_manual.main
```

### E2E Playwright (opcional)

```bash
export ADVOCACIA_E2E_PWD='sua-senha'
bench --site advocacia.local serve --port 8000 --noreload   # sem reloader
python advocacia/advocacia/tests/e2e/playwright_flow.py
```

Ver [advocacia/docs/e2e_playwright.md](./advocacia/docs/e2e_playwright.md) para requisitos e variáveis.

## Licença

MIT
