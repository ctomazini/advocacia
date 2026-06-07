# E2E Playwright — App Advocacia

Fluxo automatizado: cadastros auxiliares → Client → Legal Case → satélites → `/app/painel`.

## Variáveis

| Variável | Padrão |
|---|---|
| `E2E_BASE_URL` | `http://127.0.0.1:8000` |
| `E2E_SITE_HOST` | `advocacia.local` |
| `E2E_USER` | `Administrator` |
| `E2E_PASS` | *(obrigatório)* |

Documentos criados usam o marcador `PLAYWRIGHT_<run_id>`.

## Uso

```bash
cd /home/frappe/frappe-bench/apps/advocacia/e2e
npm install
npm run install:browsers

export E2E_PASS='sua-senha'
bench --site advocacia.local serve --port 8000 --noreload

npm test
```

Relatório JSON em `results/<run_id>/report.json`.

## Wrapper Python (deprecated)

`advocacia/advocacia/tests/e2e/playwright_flow.py` permanece como referência legada.
Prefira este pacote npm.
