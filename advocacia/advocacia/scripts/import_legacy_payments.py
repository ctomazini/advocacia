"""
Importação one-shot de boletos legados → Legal Payment (produção).

Pré-requisitos no site:
  - Legal Case (SERV-…) e Client já existem
  - Fee Agreement por serviço: usa o existente ou cria placeholder "Honorários Diretos"

Uso (recomendado):
  # 1) Simular
  bench --site SEU-SITE execute advocacia.advocacia.scripts.import_legacy_payments.run \\
    --kwargs "{'dry_run': True}"

  # 2) Importar
  bench --site SEU-SITE execute advocacia.advocacia.scripts.import_legacy_payments.run \\
    --kwargs "{'dry_run': False, 'confirm_production': True}"

NÃO pipear este arquivo no console (bench console < arquivo.py quebra funções).

Console (2 linhas, sem linha em branco entre elas):
  from advocacia.advocacia.scripts.import_legacy_payments import import_boletos
  import_boletos(dry_run=True)

Ou: exec(open("/home/frappe/criar_pagamentos.py").read())  # runner mínimo
"""

from __future__ import annotations

import hashlib

import frappe
from frappe import _
from frappe.utils import flt, getdate

from advocacia.advocacia.financeiro import TIPO_HONORARIOS

# ── Ajuste antes de rodar em produção ─────────────────────────────────────
CONFIRM_PRODUCTION = False  # obrigatório True se site contiver "prod" ou "erp."
CREATE_FEE_AGREEMENT_IF_MISSING = True
# ─────────────────────────────────────────────────────────────────────────

IMPORT_PREFIX = "LEGACY-IMPORT"

# cli = Client.name · serv = Legal Case.name
BOLETOS = [
	{"cli": "CLI-2026-0276", "serv": "SERV-2026-0378", "desc": "6 de 6", "val": 541, "dt": "2025-04-15", "st": "Vencido"},
	{"cli": "CLI-2026-0313", "serv": "SERV-2026-0384", "desc": "R$ 4.0000PAGO R$ 1000 dia 27/06", "val": 3000, "dt": "2025-07-03", "st": "Vencido"},
	{"cli": "CLI-2026-0289", "serv": "SERV-2026-0381", "desc": "5 de 6 falata R$ 500Defesa mais audiencia dia 10/02 R$ 3000Audiencia dia 30/07/2025 1500Pago R$ 300 dia 10/09", "val": 1700, "dt": "2025-07-05", "st": "Vencido"},
	{"cli": "CLI-2026-0260", "serv": "SERV-2026-0377", "desc": "um salario audiencia 17/03 Carlos Eduardo", "val": 1620, "dt": "2025-07-21", "st": "Vencido"},
	{"cli": "CLI-2026-0208", "serv": "SERV-2026-0374", "desc": "3 de 9R$ 1404 - pago R$ 1000 dia 18/09/2025. abatido mais 500, pago dia 05/06honorários processo famíliaTotal R$ 12650", "val": 310, "dt": "2025-08-17", "st": "Vencido"},
	{"cli": "CLI-2026-0287", "serv": "SERV-2026-0380", "desc": "6 de 7", "val": 2167, "dt": "2025-09-01", "st": "Vencido"},
	{"cli": "CLI-2026-0141", "serv": "SERV-2026-0372", "desc": "inventário", "val": 1000, "dt": "2025-10-14", "st": "Vencido"},
	{"cli": "CLI-2026-0298", "serv": "SERV-2026-0382", "desc": "audiencia dia 12/11/2025", "val": 1620, "dt": "2025-11-12", "st": "Vencido"},
	{"cli": "CLI-2026-0208", "serv": "SERV-2026-0374", "desc": "7 de 9honorários processo famíliaTotal R$ 12650", "val": 1405, "dt": "2025-12-17", "st": "Vencido"},
	{"cli": "CLI-2026-0287", "serv": "SERV-2026-0380", "desc": "1 de 3", "val": 500, "dt": "2026-01-10", "st": "Vencido"},
	{"cli": "CLI-2026-0208", "serv": "SERV-2026-0374", "desc": "8 de 9honorários processo famíliaTotal R$ 12650pago R$ 500 16/01", "val": 905, "dt": "2026-01-17", "st": "Vencido"},
	{"cli": "CLI-2026-0176", "serv": "SERV-2026-0373", "desc": "R$ 2.0002 de 4", "val": 500, "dt": "2026-01-20", "st": "Vencido"},
	{"cli": "CLI-2026-0071", "serv": "SERV-2026-0371", "desc": "1500 - audiencia Djulia 05/02/2026", "val": 1500, "dt": "2026-02-05", "st": "Vencido"},
	{"cli": "CLI-2026-0287", "serv": "SERV-2026-0380", "desc": "2 de 3", "val": 500, "dt": "2026-02-10", "st": "Vencido"},
	{"cli": "CLI-2026-0208", "serv": "SERV-2026-0374", "desc": "9 de 9honorários processo famíliaTotal R$ 12650", "val": 1405, "dt": "2026-02-17", "st": "Vencido"},
	{"cli": "CLI-2026-0176", "serv": "SERV-2026-0373", "desc": "R$ 2.0003 de 4", "val": 500, "dt": "2026-02-20", "st": "Vencido"},
	{"cli": "CLI-2026-0287", "serv": "SERV-2026-0380", "desc": "3 de 3. Audiencia familia", "val": 500, "dt": "2026-03-10", "st": "Vencido"},
	{"cli": "CLI-2026-0176", "serv": "SERV-2026-0373", "desc": "R$ 2.0004 de 4", "val": 500, "dt": "2026-03-20", "st": "Vencido"},
	{"cli": "CLI-2026-0336", "serv": "SERV-2026-0385", "desc": "Audiencia JULIA GOMES ROSA Dia 10/03/2026 às 10:05", "val": 1620, "dt": "2026-04-10", "st": "Vencido"},
	{"cli": "CLI-2026-0366", "serv": "SERV-2026-0389", "desc": "Total R$ 5000,0010x de R$ 500, a iniciar dia 23/04/2026 23/06; 23/07; 23/08; 23/09; 23/10; 23/11, 23/12, 23/01", "val": 4000, "dt": "2026-04-23", "st": "Vencido"},
	{"cli": "CLI-2026-0337", "serv": "SERV-2026-0386", "desc": "R$ 810 - metade defesa CREAR$ 2000 - Defesa Reclamante CassioR$ 1620 - Perícia Reclamante Edelmilson", "val": 4430, "dt": "2026-04-23", "st": "Vencido"},
	{"cli": "CLI-2026-0213", "serv": "SERV-2026-0375", "desc": "Audiência 21/05/2026. reclamante Edinaldo Maria da Silva", "val": 1620, "dt": "2026-04-27", "st": "Vencido"},
	{"cli": "CLI-2026-0257", "serv": "SERV-2026-0376", "desc": "R$ 3000 - processo cirurgia5 de 6", "val": 500, "dt": "2026-05-10", "st": "Vencido"},
	{"cli": "CLI-2026-0281", "serv": "SERV-2026-0379", "desc": "R$ 1620 - Defesa RECLAMANTE: FELIPE FERNANDES DAITXR$ 1620 - Defesa RECLAMANTE: VANESSA RODRIGUES ANCHIETA", "val": 3240, "dt": "2026-05-26", "st": "Vencido"},
	{"cli": "CLI-2026-0257", "serv": "SERV-2026-0376", "desc": "R$ 3000 - processo cirurgia6 de 6", "val": 500, "dt": "2026-06-10", "st": "Pendente"},
	{"cli": "CLI-2026-0308", "serv": "SERV-2026-0383", "desc": "R$ 20.000 + R$ 2000R$ 4400,002 de 5R$ 2800 para o reclamante", "val": 4400, "dt": "2026-06-15", "st": "Pendente"},
	{"cli": "CLI-2026-0355", "serv": "SERV-2026-0387", "desc": "R$ 20004 de 4", "val": 500, "dt": "2026-06-20", "st": "Pendente"},
	{"cli": "CLI-2026-0368", "serv": "SERV-2026-0390", "desc": "Defesa R$ 3500PAGO 1000 15/05parcela 2 de 3", "val": 1000, "dt": "2026-06-20", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "processo de familia separação/reconhecimento4 de 8", "val": 500, "dt": "2026-06-25", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "6x de R$ 50025/06; ; 25/07;  25/08; 25/09; 25/10", "val": 2500, "dt": "2026-06-25", "st": "Vencido"},
	{"cli": "CLI-2026-0308", "serv": "SERV-2026-0383", "desc": "R$ 20.000 + R$ 2000R$ 4400,003 de 5R$ 2800 para o reclamante", "val": 4400, "dt": "2026-07-15", "st": "Pendente"},
	{"cli": "CLI-2026-0368", "serv": "SERV-2026-0390", "desc": "ultima parcela defesa familia", "val": 1500, "dt": "2026-07-20", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "processo de familia separação/reconhecimento5 de 8", "val": 500, "dt": "2026-07-25", "st": "Pendente"},
	{"cli": "CLI-2026-0355", "serv": "SERV-2026-0387", "desc": "audiencia dia 20/04/2026R$ 1620", "val": 540, "dt": "2026-07-25", "st": "Pendente"},
	{"cli": "CLI-2026-0308", "serv": "SERV-2026-0383", "desc": "R$ 20.000 + R$ 2000R$ 4400,004 de 5R$ 2800 para o reclamante", "val": 4400, "dt": "2026-08-15", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "processo de familia separação/reconhecimento6 de 8", "val": 500, "dt": "2026-08-25", "st": "Pendente"},
	{"cli": "CLI-2026-0355", "serv": "SERV-2026-0387", "desc": "audiencia dia 20/04/2026R$ 16202 de 3", "val": 540, "dt": "2026-08-25", "st": "Pendente"},
	{"cli": "CLI-2026-0308", "serv": "SERV-2026-0383", "desc": "R$ 20.000 + R$ 2000R$ 4400,005 de 5R$ 2800 para o reclamante", "val": 4400, "dt": "2026-09-15", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "processo de familia separação/reconhecimento7 de 8", "val": 500, "dt": "2026-09-25", "st": "Pendente"},
	{"cli": "CLI-2026-0355", "serv": "SERV-2026-0387", "desc": "audiencia dia 20/04/2026R$ 16203 de 3", "val": 540, "dt": "2026-09-25", "st": "Pendente"},
	{"cli": "CLI-2026-0356", "serv": "SERV-2026-0388", "desc": "processo de familia separação/reconhecimento8 de 8", "val": 500, "dt": "2026-10-25", "st": "Pendente"},
]


def _guard_production(confirm_production: bool) -> None:
	site = frappe.local.site or ""
	if site and ("prod" in site or "erp." in site) and not confirm_production:
		frappe.throw(
			_(
				"Site parece produção ({0}). Passe confirm_production=True ou defina CONFIRM_PRODUCTION=True."
			).format(site),
			title=_("Importação bloqueada"),
		)


def _origin_id(b: dict) -> str:
	raw = f"{b['serv']}|{b['dt']}|{flt(b['val'])}|{b['desc'][:120]}"
	digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
	return f"{IMPORT_PREFIX}-{digest}"


def _resolve_fee_agreement(legal_case: str, client: str, dry_run: bool) -> str | None:
	acordo = frappe.db.get_value(
		"Fee Agreement",
		{"legal_case": legal_case},
		"name",
		order_by="modified desc",
	)
	if acordo:
		return acordo
	if not CREATE_FEE_AGREEMENT_IF_MISSING:
		return None
	if dry_run:
		return f"(novo acordo para {legal_case})"
	doc = frappe.get_doc(
		{
			"doctype": "Fee Agreement",
			"legal_case": legal_case,
			"client": client,
			"fee_mode": "Honorários Diretos",
			"billing_type": "Valor fixo",
			"status": "Vigente",
			"remarks": "Acordo placeholder — importação de boletos legados.",
		}
	)
	doc.insert(ignore_permissions=True)  # setup: importação one-shot legado
	return doc.name


def _validate_row(b: dict) -> tuple[str, str]:
	legal_case = b["serv"]
	if not frappe.db.exists("Legal Case", legal_case):
		raise frappe.ValidationError(_("Legal Case {0} não existe").format(legal_case))

	client_on_case = frappe.db.get_value("Legal Case", legal_case, "client")
	if not client_on_case:
		raise frappe.ValidationError(_("Legal Case {0} sem cliente").format(legal_case))

	if b["cli"] and b["cli"] != client_on_case:
		if not frappe.db.exists("Client", b["cli"]):
			raise frappe.ValidationError(_("Client {0} não existe").format(b["cli"]))
		frappe.logger().warning(
			"Importação {0}: CLI planilha ({1}) ≠ cliente do serviço ({2}); usa o do serviço.",
			_origin_id(b),
			b["cli"],
			client_on_case,
		)

	status = b["st"]
	if status not in ("Pendente", "Vencido", "Recebido", "Cancelado", "Renegociado", "Repassado"):
		raise frappe.ValidationError(_("Status inválido: {0}").format(status))

	return legal_case, client_on_case


def import_boletos(dry_run: bool = True, confirm_production: bool | None = None) -> dict:
	"""Importa BOLETOS como Legal Payment. Idempotente via installment_origin_id."""
	if confirm_production is None:
		confirm_production = CONFIRM_PRODUCTION
	_guard_production(confirm_production)

	stats = {"created": 0, "skipped": 0, "errors": 0, "dry_run": dry_run}

	for b in BOLETOS:
		origin_id = _origin_id(b)
		try:
			if frappe.db.exists("Legal Payment", {"installment_origin_id": origin_id}):
				stats["skipped"] += 1
				continue

			legal_case, client = _validate_row(b)
			acordo = _resolve_fee_agreement(legal_case, client, dry_run)
			if not acordo:
				raise frappe.ValidationError(
					_("Sem Fee Agreement para {0} e CREATE_FEE_AGREEMENT_IF_MISSING=False").format(
						legal_case
					)
				)

			if dry_run:
				print(
					f"[DRY] {origin_id} → {legal_case} | R$ {flt(b['val'])} | {b['dt']} | {b['st']}"
				)
				stats["created"] += 1
				continue

			doc = frappe.get_doc(
				{
					"doctype": "Legal Payment",
					"origin_type": TIPO_HONORARIOS,
					"fee_agreement": acordo,
					"legal_case": legal_case,
					"client": client,
					"description": b["desc"],
					"amount": flt(b["val"]),
					"due_date": getdate(b["dt"]),
					"status": b["st"],
					"manual_override": 1,
					"installment_origin_id": origin_id,
				}
			)
			doc.insert(ignore_permissions=True)  # setup: importação one-shot legado
			stats["created"] += 1
		except Exception as exc:
			stats["errors"] += 1
			print(f"ERRO {origin_id} serv={b.get('serv')} — {exc}")

	if not dry_run:
		frappe.db.commit()  # setup: importação one-shot legado

	summary = (
		f"{'[DRY RUN] ' if dry_run else ''}"
		f"{stats['created']} criados, {stats['skipped']} já existiam, {stats['errors']} erros"
	)
	print(summary)
	return stats


def run(dry_run: bool = True, confirm_production: bool | None = None):
	"""Entry point para bench execute."""
	return import_boletos(dry_run=dry_run, confirm_production=confirm_production)
