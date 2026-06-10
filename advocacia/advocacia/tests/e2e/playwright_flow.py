#!/usr/bin/env python3
"""
Sessão E2E Playwright — App Advocacia.

Preenche formulários na UI com dados fictícios (_PW_E2E_) e remove apenas
os documentos criados nesta execução. Não altera registros existentes.

Requisitos:
  pip install playwright   # já incluso no bench env, se instalado
  playwright install chromium
  sudo playwright install-deps	 # libnspr4 etc. no Linux

Uso:
  export ADVOCACIA_E2E_PWD='sua-senha'
  export ADVOCACIA_E2E_SITE='advocacia.local'	# opcional
  export ADVOCACIA_E2E_URL='http://127.0.0.1:8000'	# opcional
  export FRAPPE_BENCH_PATH='/home/frappe/frappe-bench'	# opcional

  bench --site advocacia.local serve --port 8000 --noreload

  python advocacia/advocacia/tests/e2e/playwright_flow.py

Deprecated: prefira o pacote npm em ../../e2e/ (`npm test` após `npm install`).
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

MARKER = "_PW_E2E_"
RUN_ID = datetime.now().strftime("%Y%m%d%H%M%S")

BASE_URL = os.environ.get("ADVOCACIA_E2E_URL", "http://127.0.0.1:8000")
SITE_HOST = os.environ.get("ADVOCACIA_E2E_HOST", "advocacia.local")
SITE_NAME = os.environ.get("ADVOCACIA_E2E_SITE", "advocacia.local")
ADMIN_USER = os.environ.get("ADVOCACIA_E2E_USER", "Administrator")
ADMIN_PWD = os.environ.get("ADVOCACIA_E2E_PWD", "")
REPORT_PATH = os.environ.get(
	"ADVOCACIA_E2E_REPORT",
	f"/tmp/advocacia_playwright_report_{RUN_ID}.json",
)

DOCTYPES_ORDER = [
	"Jurisdiction",
	"Court",
	"Court Branch",
	"Case Phase",
	"Client",
	"Legal Case",
	"Fee Agreement",
	"Service Record",
	"Hearing",
	"Deadline",
	"Legal Task",
	"Case Communication",
	"Time Entry",
	"Court Cost",
	"Office Expense",
	"Document Template",
	"Document Kit",
]


def resolve_bench_path() -> str:
	env_path = os.environ.get("FRAPPE_BENCH_PATH")
	if env_path and os.path.isdir(os.path.join(env_path, "sites")):
		return env_path
	path = os.path.abspath(os.path.dirname(__file__))
	for _ in range(10):
		if os.path.isdir(os.path.join(path, "sites")):
			return path
		parent = os.path.dirname(path)
		if parent == path:
			break
		path = parent
	return "/home/frappe/frappe-bench"


BENCH_PATH = resolve_bench_path()
sys.path.insert(0, os.path.join(BENCH_PATH, "apps", "frappe"))
sys.path.insert(0, os.path.join(BENCH_PATH, "apps", "advocacia"))
os.chdir(os.path.join(BENCH_PATH, "sites"))

import frappe
from frappe.app import application
from frappe.utils import add_days, today
from werkzeug.test import Client

from advocacia.advocacia.tests.test_setup import _gerar_cpf_valido
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright


@dataclass
class StepResult:
	doctype: str
	status: str
	detail: str = ""
	docname: str = ""


@dataclass
class SessionReport:
	started_at: str = field(default_factory=lambda: datetime.now().isoformat())
	finished_at: str = ""
	steps: list[StepResult] = field(default_factory=list)
	created: dict[str, str] = field(default_factory=dict)

	def add(self, step: StepResult) -> None:
		self.steps.append(step)
		if step.status == "ok" and step.docname:
			self.created[step.doctype] = step.docname


report = SessionReport()


def init_frappe() -> None:
	frappe.init(site=SITE_NAME, sites_path=".")
	frappe.connect()


def slug(doctype: str) -> str:
	return doctype.lower().replace(" ", "-")


def format_cpf(digits: str) -> str:
	return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def wsgi_login() -> list[dict]:
	if not ADMIN_PWD:
		raise RuntimeError("Defina ADVOCACIA_E2E_PWD com a senha do usuário de teste.")

	client = Client(application, use_cookies=True)
	res = client.post(
		"/api/method/login",
		data={"usr": ADMIN_USER, "pwd": ADMIN_PWD},
		headers={"Host": SITE_HOST},
	)
	if res.status_code != 200:
		raise RuntimeError(
			f"Login WSGI falhou: {res.status_code} {res.get_data(as_text=True)[:200]}"
		)
	cookies = []
	for header in res.headers.getlist("Set-Cookie"):
		name, _, rest = header.partition("=")
		value = rest.split(";", 1)[0]
		cookies.append(
			{
				"name": name.strip(),
				"value": value.strip(),
				"domain": SITE_HOST.split(":")[0],
				"path": "/",
			}
		)
	return cookies


def wait_form_ready(page) -> None:
	page.wait_for_selector(".form-layout", timeout=30000)
	page.wait_for_function("() => window.cur_frm && cur_frm.doc", timeout=30000)
	time.sleep(0.5)


def fill_input(page, fieldname: str, value: str) -> None:
	loc = page.locator(f'.frappe-control[data-fieldname="{fieldname}"] input:visible').first
	loc.click()
	loc.fill(value)


def fill_select(page, fieldname: str, value: str) -> None:
	page.locator(f'.frappe-control[data-fieldname="{fieldname}"] select').select_option(value)


def fill_link(page, fieldname: str, value: str) -> None:
	loc = page.locator(f'.frappe-control[data-fieldname="{fieldname}"] input:visible').first
	loc.click()
	loc.fill(value)
	page.keyboard.press("Tab")
	time.sleep(0.8)


def fill_textarea(page, fieldname: str, value: str) -> None:
	page.locator(f'.frappe-control[data-fieldname="{fieldname}"] textarea').fill(value)


def save_form(page) -> str:
	page.locator(".primary-action").click()
	page.wait_for_function(
		"""() => {
			const pill = document.querySelector('.indicator-pill');
			return pill && /Salvo|Saved|Submitted|Submetido/i.test(pill.textContent || '');
		}""",
		timeout=45000,
	)
	name = page.evaluate("() => (cur_frm && cur_frm.docname) || ''")
	if not name:
		raise RuntimeError("Salvou mas docname não encontrado")
	return name


def open_new(page, doctype: str) -> None:
	page.goto(f"{BASE_URL}/app/{slug(doctype)}/new", wait_until="domcontentloaded")
	wait_form_ready(page)


def run_step(doctype: str, fn) -> None:
	try:
		docname = fn()
		report.add(StepResult(doctype, "ok", docname=docname))
		print(f"  OK  {doctype}: {docname}")
	except PlaywrightTimeout as exc:
		report.add(StepResult(doctype, "fail", detail=f"timeout: {exc}"))
		print(f"  FAIL {doctype}: timeout")
	except Exception as exc:
		report.add(StepResult(doctype, "fail", detail=str(exc)[:300]))
		print(f"  FAIL {doctype}: {exc}")


def cleanup_created() -> None:
	init_frappe()
	for dt in reversed(DOCTYPES_ORDER):
		name = report.created.get(dt)
		if not name:
			continue
		try:
			if frappe.db.exists(dt, name):
				frappe.delete_doc(dt, name, force=1, ignore_permissions=True)
				print(f"  cleanup {dt} {name}")
		except Exception as exc:
			print(f"  cleanup skip {dt} {name}: {exc}")
	frappe.db.commit()


def main() -> int:
	init_frappe()

	print(f"Advocacia Playwright E2E — {RUN_ID}")
	print(f"URL={BASE_URL} Host={SITE_HOST} Site={SITE_NAME}")

	cookies = wsgi_login()
	cpf_masked = format_cpf(_gerar_cpf_valido())

	names = {
		"jurisdiction": f"Jurisdiction E2E {RUN_ID}",
		"court": f"Court E2E {RUN_ID}",
		"court_branch_link": f"Court Branch E2E {RUN_ID}",
		"fase": f"Fase E2E {RUN_ID}",
		"client": f"Client {MARKER} {RUN_ID}",
	}

	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context(
			base_url=BASE_URL,
			extra_http_headers={"Host": SITE_HOST},
		)
		context.add_cookies(cookies)
		page = context.new_page()
		page.set_default_timeout(30000)

		page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
		if "/login" in page.url:
			raise RuntimeError("Sessão não autenticada — redirecionou para login")

		print("\n--- Cadastro auxiliar ---")

		run_step("Jurisdiction", lambda: (
			open_new(page, "Jurisdiction"),
			fill_input(page, "jurisdiction_name", names["jurisdiction"]),
			fill_select(page, "uf", "SP"),
			fill_input(page, "city", "Sao Paulo"),
			save_form(page),
		)[-1])

		run_step("Court", lambda: (
			open_new(page, "Court"),
			fill_input(page, "court_name", names["court"]),
			fill_input(page, "abbreviation", f"T{RUN_ID[-4:]}"),
			fill_select(page, "jurisdiction", "Estadual"),
			save_form(page),
		)[-1])

		run_step("Court Branch", lambda: (
			open_new(page, "Court Branch"),
			fill_input(page, "court_branch_name", names["court_branch_link"]),
			fill_link(page, "jurisdiction", names["jurisdiction"]),
			fill_select(page, "type", "Cível"),
			save_form(page),
		)[-1])

		run_step("Case Phase", lambda: (
			open_new(page, "Case Phase"),
			fill_input(page, "case_phase_name", names["fase"]),
			fill_input(page, "sort_order", "99"),
			save_form(page),
		)[-1])

		print("\n--- Fluxo principal ---")

		run_step("Client", lambda: (
			open_new(page, "Client"),
			fill_select(page, "person_type", "Pessoa Física"),
			fill_input(page, "client_name", names["client"]),
			fill_input(page, "cpf", cpf_masked),
			fill_input(page, "email", f"e2e{RUN_ID}@exemplo.com"),
			save_form(page),
		)[-1])

		cliente_name = report.created.get("Client", names["client"])

		run_step("Legal Case", lambda: (
			open_new(page, "Legal Case"),
			fill_link(page, "client", cliente_name),
			fill_select(page, "type", "Consultoria"),
			fill_textarea(page, "remarks", f"{MARKER} servico {RUN_ID}"),
			save_form(page),
		)[-1])

		servico_name = report.created.get("Legal Case", "")

		run_step("Fee Agreement", lambda: (
			open_new(page, "Fee Agreement"),
			fill_link(page, "legal_case", servico_name),
			fill_select(page, "fee_mode", "Honorários Diretos"),
			fill_select(page, "billing_type", "Valor fixo"),
			fill_input(page, "total_agreement_value", "5000"),
			fill_textarea(page, "remarks", f"{MARKER} acordo {RUN_ID}"),
			save_form(page),
		)[-1])

		run_step("Service Record", lambda: (
			open_new(page, "Service Record"),
			fill_link(page, "legal_case", servico_name),
			fill_textarea(page, "remarks", f"{MARKER} atos {RUN_ID}"),
			save_form(page),
		)[-1])

		run_step("Hearing", lambda: (
			open_new(page, "Hearing"),
			fill_link(page, "legal_case", servico_name),
			page.locator('.frappe-control[data-fieldname="hearing_datetime"] input:visible').first.fill(
				f"{today()} 14:00:00"
			),
			fill_select(page, "type", "Conciliação"),
			fill_select(page, "modality", "Presencial"),
			fill_textarea(page, "remarks", f"{MARKER} audiencia {RUN_ID}"),
			save_form(page),
		)[-1])

		run_step("Deadline", lambda: (
			open_new(page, "Deadline"),
			fill_link(page, "legal_case", servico_name),
			fill_input(page, "description", f"{MARKER} prazo {RUN_ID}"),
			page.locator('.frappe-control[data-fieldname="due_date"] input:visible').first.fill(
				add_days(today(), 7)
			),
			fill_select(page, "priority", "Média"),
			save_form(page),
		)[-1])

		run_step("Legal Task", lambda: (
			open_new(page, "Legal Task"),
			fill_link(page, "legal_case", servico_name),
			fill_input(page, "subject", f"{MARKER} tarefa {RUN_ID}"),
			page.locator('.frappe-control[data-fieldname="due_date"] input:visible').first.fill(
				add_days(today(), 3)
			),
			save_form(page),
		)[-1])

		run_step("Case Communication", lambda: (
			open_new(page, "Case Communication"),
			fill_link(page, "legal_case", servico_name),
			fill_input(page, "subject", f"{MARKER} comunicacao {RUN_ID}"),
			fill_select(page, "type", "Email"),
			save_form(page),
		)[-1])

		run_step("Time Entry", lambda: (
			open_new(page, "Time Entry"),
			fill_link(page, "legal_case", servico_name),
			page.locator('.frappe-control[data-fieldname="entry_date"] input:visible').first.fill(today()),
			fill_input(page, "duration_minutes", "60"),
			fill_input(page, "activity", f"{MARKER} horas {RUN_ID}"),
			save_form(page),
		)[-1])

		run_step("Court Cost", lambda: (
			open_new(page, "Court Cost"),
			fill_link(page, "legal_case", servico_name),
			fill_input(page, "description", f"{MARKER} custa {RUN_ID}"),
			fill_input(page, "amount", "150"),
			page.locator('.frappe-control[data-fieldname="payment_date"] input:visible').first.fill(
				today()
			),
			save_form(page),
		)[-1])

		run_step("Office Expense", lambda: (
			open_new(page, "Office Expense"),
			fill_input(page, "description", f"{MARKER} despesa {RUN_ID}"),
			fill_input(page, "amount", "200"),
			page.locator('.frappe-control[data-fieldname="due_date"] input:visible').first.fill(
				add_days(today(), 10)
			),
			save_form(page),
		)[-1])

		# Exigem anexo — falha esperada sem upload de arquivo
		run_step("Document Template", lambda: (
			open_new(page, "Document Template"),
			fill_input(page, "title", f"{MARKER} template {RUN_ID}"),
			fill_select(page, "document_type", "Contrato"),
			save_form(page),
		)[-1])

		run_step("Document Kit", lambda: (
			open_new(page, "Document Kit"),
			fill_input(page, "title", f"{MARKER} kit {RUN_ID}"),
			save_form(page),
		)[-1])

		if servico_name:
			try:
				page.goto(f"{BASE_URL}/app/servico/{servico_name}", wait_until="domcontentloaded")
				wait_form_ready(page)
				page.wait_for_selector(".form-dashboard", timeout=15000)
				report.add(StepResult("Connections (Legal Case)", "ok", docname=servico_name))
				print("	 OK	 Connections (Legal Case): dashboard visível")
			except Exception as exc:
				report.add(StepResult("Connections (Legal Case)", "fail", detail=str(exc)[:200]))
				print(f"  FAIL Connections: {exc}")

		browser.close()

	report.finished_at = datetime.now().isoformat()
	ok = sum(1 for s in report.steps if s.status == "ok")
	fail = sum(1 for s in report.steps if s.status == "fail")

	with open(REPORT_PATH, "w", encoding="utf-8") as fh:
		json.dump(
			{
				"run_id": RUN_ID,
				"marker": MARKER,
				"started_at": report.started_at,
				"finished_at": report.finished_at,
				"summary": {"ok": ok, "fail": fail, "total": len(report.steps)},
				"steps": [s.__dict__ for s in report.steps],
				"created": report.created,
			},
			fh,
			ensure_ascii=False,
			indent=2,
		)

	print(f"\n--- Resumo: {ok} OK / {fail} FAIL ---")
	print(f"Relatório: {REPORT_PATH}")

	print("\n--- Cleanup documentos _PW_E2E_ ---")
	cleanup_created()

	return 0 if fail == 0 else 1


if __name__ == "__main__":
	raise SystemExit(main())
