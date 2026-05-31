# Advocacia

Aplicativo Frappe v16 para gestão jurídica de escritórios de advocacia no Brasil: clientes, serviços/processos, honorários, pagamentos, atos, prazos, audiências, despesas operacionais, painel operacional e geração de documentos (.docx).

**Versão:** 0.5.0 · **Branch:** `frappe-v16`

Documentação técnica completa: [CODEBASE_FINAL.md](./CODEBASE_FINAL.md)

## Requisitos

- [Frappe Bench](https://github.com/frappe/bench) com Frappe v16.x
- Python 3.12+
- Node.js **20+** (Frappe v16.19 recomenda **Node ≥24** para `bench build`)
- MariaDB 10.6+
- Dependência Python: `docxtpl>=0.18.0` (instalada via `pyproject.toml`)

## Instalação

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/ctomazini/advocacia.git --branch frappe-v16
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

Suíte atual: **120 testes** (`FrappeTestCase`).

## Desenvolvimento

Após alterar DocType JSON: `bench --site seu-site.local migrate`  
Após alterar JS de DocType: `bench --site seu-site.local clear-cache`  
Após alterar `public/js/`: `bench build --app advocacia`

## Licença

MIT
