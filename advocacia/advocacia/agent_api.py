"""Read-only aggregated API endpoints for AI agents."""

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, today

from advocacia.advocacia.painel._helpers import user_is_advocacia_manager
from advocacia.advocacia.titulos import get_cliente_nome

ACTIVE_CASE_STATUSES = ("Em andamento",)

_FINANCIAL_SUMMARY_KEYS = (
	"fee_agreement_value",
	"fee_agreement_status",
	"amount_receivable",
	"pending_payments_count",
	"court_costs_total",
	"court_costs_reimbursable",
)


@frappe.whitelist()
def get_active_cases() -> list[dict]:
	"""Return active Legal Cases with satellite counts."""
	frappe.has_permission("Legal Case", "read", throw=True)

	cases = frappe.get_all(
		"Legal Case",
		filters={"status": ["in", list(ACTIVE_CASE_STATUSES)]},
		fields=["name", "title", "client", "tipo", "numero_processo", "area", "status"],
		order_by="modified desc",
		limit_page_length=100,
	)

	client_names = {
		row.name: row.nome
		for row in frappe.get_all(
			"Client",
			filters={"name": ["in", [case.client for case in cases if case.client]]},
			fields=["name", "nome"],
			limit_page_length=100,
		)
	}

	for case in cases:
		case["client_name"] = client_names.get(case.client) or get_cliente_nome(case.client)
		case["hearings"] = frappe.db.count("Hearing", {"legal_case": case.name})
		case["deadlines"] = frappe.db.count(
			"Deadline", {"legal_case": case.name, "status": "Pendente"}
		)
		case["tasks"] = frappe.db.count(
			"Legal Task",
			{"legal_case": case.name, "status": ["in", ["Pendente", "Em Andamento"]]},
		)

	return cases


def _case_financial_summary(case_name: str) -> dict:
	fee_agreement = frappe.get_all(
		"Fee Agreement",
		filters={"legal_case": case_name, "status": ["!=", "Cancelado"]},
		fields=["name", "valor_total_do_acordo", "status"],
		order_by="modified desc",
		limit=1,
	)
	payments = frappe.get_all(
		"Legal Payment",
		filters={"legal_case": case_name, "status": ["in", ["Pendente", "Vencido"]]},
		fields=["valor"],
		limit_page_length=100,
	)
	court_costs = frappe.get_all(
		"Court Cost",
		filters={"legal_case": case_name, "status": ["!=", "Cancelado"]},
		fields=["valor", "repassar_cliente"],
		limit_page_length=200,
	)

	agreement_value = flt(fee_agreement[0].valor_total_do_acordo) if fee_agreement else 0
	reimbursable = sum(
		flt(row.valor) for row in court_costs if row.repassar_cliente and row.valor
	)
	total_costs = sum(flt(row.valor) for row in court_costs if row.valor)

	return {
		"fee_agreement_value": agreement_value,
		"fee_agreement_status": fee_agreement[0].status if fee_agreement else None,
		"amount_receivable": sum(flt(row.valor) for row in payments),
		"pending_payments_count": len(payments),
		"court_costs_total": total_costs,
		"court_costs_reimbursable": reimbursable,
	}


@frappe.whitelist()
def get_case_summary(case_name: str) -> dict:
	"""Return detailed summary of a Legal Case."""
	frappe.has_permission("Legal Case", "read", doc=case_name, throw=True)

	case = frappe.get_doc("Legal Case", case_name)
	summary = {
		"name": case.name,
		"title": case.title,
		"client": case.client,
		"client_name": get_cliente_nome(case.client),
		"tipo": case.tipo,
		"status": case.status,
		"numero_processo": case.numero_processo,
		"area": case.area,
	}

	summary["deadlines"] = frappe.get_all(
		"Deadline",
		filters={"legal_case": case_name, "status": "Pendente"},
		fields=["name", "title", "data_prazo", "prioridade"],
		order_by="data_prazo asc",
		limit_page_length=20,
	)

	summary["hearings"] = frappe.get_all(
		"Hearing",
		filters={"legal_case": case_name, "status_aud": ["!=", "Cancelada"]},
		fields=["name", "title", "data_hora", "tipo", "modalidade"],
		order_by="data_hora asc",
		limit_page_length=10,
	)

	summary["tasks"] = frappe.get_all(
		"Legal Task",
		filters={"legal_case": case_name, "status": ["in", ["Pendente", "Em Andamento"]]},
		fields=["name", "titulo", "status", "data_limite", "prioridade"],
		order_by="data_limite asc",
		limit_page_length=20,
	)

	if user_is_advocacia_manager():
		summary.update(_case_financial_summary(case_name))
		summary["fee_agreements"] = frappe.get_all(
			"Fee Agreement",
			filters={"legal_case": case_name},
			fields=["name", "title", "valor_total_do_acordo", "status"],
			limit_page_length=10,
		)
	else:
		for key in _FINANCIAL_SUMMARY_KEYS:
			summary.pop(key, None)
		summary["financial_restricted"] = True

	return summary


@frappe.whitelist()
def get_court_costs_by_type(case_name: str) -> dict:
	"""Aggregate court costs by type for a Legal Case — Advocacia Manager only."""
	frappe.has_permission("Legal Case", "read", doc=case_name, throw=True)
	if not user_is_advocacia_manager():
		frappe.throw(_("Sem permissão"), frappe.PermissionError)
	frappe.has_permission("Court Cost", "read", throw=True)

	rows = frappe.get_all(
		"Court Cost",
		filters={"legal_case": case_name, "status": ["!=", "Cancelado"]},
		fields=["tipo", "valor"],
		limit_page_length=500,
	)
	totals: dict[str, float] = {}
	for row in rows:
		key = row.tipo or "Outros"
		totals[key] = totals.get(key, 0) + flt(row.valor)

	categories = [
		{"cost_type": key, "amount": amount}
		for key, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)
	]
	return {
		"case": case_name,
		"categories": categories,
		"total": sum(flt(row["amount"]) for row in categories),
	}


@frappe.whitelist()
def get_financial_overview() -> dict:
	"""Aggregated financial data — Advocacia Manager only."""
	if not user_is_advocacia_manager():
		frappe.throw(_("Sem permissão"), frappe.PermissionError)
	frappe.has_permission("Legal Payment", "read", throw=True)

	hoje = getdate(today())
	mes_inicio = hoje.replace(day=1)
	mes_fim = add_months(mes_inicio, 1)

	overview = {
		"overdue": frappe.db.count("Legal Payment", {"status": "Vencido"}),
		"pending": frappe.db.count("Legal Payment", {"status": "Pendente"}),
		"received_this_month": frappe.db.count(
			"Legal Payment",
			{"status": "Recebido", "data_recebimento": ["between", [mes_inicio, mes_fim]]},
		),
	}

	overdue_val = frappe.db.sql(
		"SELECT COALESCE(SUM(valor), 0) FROM `tabLegal Payment` WHERE status = 'Vencido'",
		as_list=True,
	)
	overview["overdue_amount"] = flt(overdue_val[0][0]) if overdue_val else 0

	received_val = frappe.db.sql(
		"""SELECT COALESCE(SUM(valor_recebido), 0) FROM `tabLegal Payment`
		WHERE status = 'Recebido' AND data_recebimento BETWEEN %s AND %s""",
		(mes_inicio, mes_fim),
		as_list=True,
	)
	overview["received_amount"] = flt(received_val[0][0]) if received_val else 0

	return overview
