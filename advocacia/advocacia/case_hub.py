"""Hub de dados por serviço — alimenta painéis visuais do Legal Case."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.utils import date_diff, flt, getdate, today

HUB_LIMIT = 50
HUB_LIMIT_SMALL = 20

DONE_DEADLINE_STATUSES = frozenset({"Concluído", "Concluida", "Cumprido", "Cancelado"})
RECEIVED_PAYMENT_STATUSES = frozenset({"Recebido", "Repassado"})


def _is_manager() -> bool:
	return "Advocacia Manager" in frappe.get_roles()


def _status_color(status: str | None) -> str:
	mapping = {
		"Recebido": "green",
		"Repassado": "green",
		"Realizada": "green",
		"Concluída": "green",
		"Concluído": "green",
		"Pendente": "orange",
		"Agendada": "blue",
		"Em Andamento": "blue",
		"Vencido": "red",
		"Vencida": "red",
		"Adiada": "orange",
		"Cancelada": "gray",
		"Cancelado": "gray",
	}
	return mapping.get(status or "", "gray")


def _deadline_urgency(due_date, status: str | None) -> tuple[int | None, str]:
	if not due_date:
		return None, "normal"
	if status in DONE_DEADLINE_STATUSES:
		return None, "done"
	diff = date_diff(getdate(due_date), getdate(today()))
	if diff < 0:
		return diff, "overdue"
	if diff <= 7:
		return diff, "urgent"
	return diff, "normal"


def _hearing_urgency(hearing_datetime, status: str | None) -> str:
	if status in ("Realizada", "Cancelada"):
		return "done"
	if not hearing_datetime:
		return "normal"
	event_date = getdate(hearing_datetime)
	current = getdate(today())
	diff = date_diff(event_date, current)
	if diff < 0:
		return "past"
	if diff == 0:
		return "today"
	if diff <= 7:
		return "upcoming"
	return "normal"


@frappe.whitelist()
def get_case_hub_data(case: str) -> dict:
	"""Agrega satélites do serviço para os painéis do hub."""
	frappe.has_permission("Legal Case", "read", doc=case, throw=True)

	data: dict = {
		"phases": get_phases(case),
		"hearings": get_hearings(case),
		"deadlines": get_deadlines(case),
		"tasks": get_tasks(case),
		"communications": get_communications(case),
		"service_records": get_service_records(case),
		"time_entries": get_time_entries(case),
		"document_kits": get_document_kits(case),
		"documents": get_case_documents(case),
		"financial": get_financial(case) if _is_manager() else None,
	}
	return data


@frappe.whitelist()
def get_case_counts(case: str) -> dict:
	"""Contadores rápidos de satélites — barra de pills."""
	frappe.has_permission("Legal Case", "read", doc=case, throw=True)

	counts = {
		"phases": 1 if frappe.db.get_value("Legal Case", case, "case_phase") else 0,
		"hearings": frappe.db.count("Hearing", {"legal_case": case}),
		"deadlines": frappe.db.count("Deadline", {"legal_case": case}),
		"tasks": frappe.db.count(
			"Legal Task",
			{"legal_case": case, "status": ["not in", ["Concluída", "Cancelada"]]},
		),
		"communications": frappe.db.count("Case Communication", {"legal_case": case}),
		"service_records": frappe.db.count("Service Record", {"legal_case": case}),
		"time_entries": frappe.db.count("Time Entry", {"legal_case": case}),
		"documents": frappe.db.count("Case Document", {"legal_case": case}),
		"document_kits": frappe.db.count("Document Kit", {"enabled": 1}),
		"installments": _count_installments(case),
		"payments": frappe.db.count("Legal Payment", {"legal_case": case}),
		"court_costs": frappe.db.count("Court Cost", {"legal_case": case}),
		"fee_agreements": frappe.db.count("Fee Agreement", {"legal_case": case}),
	}

	if not _is_manager():
		for key in ("installments", "payments", "court_costs", "fee_agreements"):
			counts.pop(key, None)

	return counts


def _count_installments(case_name: str) -> int:
	inst = frappe.qb.DocType("Fee Installment")
	agr = frappe.qb.DocType("Fee Agreement")
	result = (
		frappe.qb.from_(inst)
		.join(agr)
		.on(inst.parent == agr.name)
		.select(Count(inst.name))
		.where(agr.legal_case == case_name)
	).run()
	return int(result[0][0] if result else 0)


def get_phases(case_name: str) -> list[dict]:
	"""Fase processual atual (cadastro auxiliar — sem histórico por caso)."""
	phase_link = frappe.db.get_value("Legal Case", case_name, "case_phase")
	if not phase_link:
		return []
	row = frappe.db.get_value(
		"Case Phase",
		phase_link,
		["name", "case_phase_name", "sort_order"],
		as_dict=True,
	)
	if not row:
		return []
	row["is_current"] = True
	return [row]


def get_hearings(case_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Hearing",
		filters={"legal_case": case_name},
		fields=[
			"name",
			"title",
			"hearing_datetime",
			"type",
			"modality",
			"status",
			"outcome",
		],
		order_by="hearing_datetime asc",
		limit=HUB_LIMIT,
	)
	for row in rows:
		row["urgency"] = _hearing_urgency(row.hearing_datetime, row.status)
		row["status_color"] = _status_color(row.status)
	return rows


def get_deadlines(case_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Deadline",
		filters={"legal_case": case_name},
		fields=["name", "title", "due_date", "status", "priority", "description"],
		order_by="due_date asc",
		limit=HUB_LIMIT,
	)
	for row in rows:
		days, urgency = _deadline_urgency(row.due_date, row.status)
		row["days_remaining"] = days
		row["urgency"] = urgency
		row["status_color"] = _status_color(row.status)
	return rows


def get_tasks(case_name: str) -> list[dict]:
	priority_order = {"Urgente": 0, "Alta": 1, "Normal": 2}
	rows = frappe.get_all(
		"Legal Task",
		filters={"legal_case": case_name, "status": ["not in", ["Concluída", "Cancelada"]]},
		fields=["name", "subject", "status", "priority", "due_date", "responsible"],
		order_by="due_date asc",
		limit=HUB_LIMIT_SMALL,
	)
	rows.sort(key=lambda row: (priority_order.get(row.priority or "Normal", 9), row.due_date or ""))
	current = getdate(today())
	for row in rows:
		row["status_color"] = _status_color(row.status)
		if row.due_date:
			row["days_remaining"] = date_diff(getdate(row.due_date), current)
		else:
			row["days_remaining"] = None
	return rows


def get_communications(case_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Case Communication",
		filters={"legal_case": case_name},
		fields=["name", "title", "subject", "type", "communication_date", "summary"],
		order_by="communication_date desc",
		limit=HUB_LIMIT_SMALL,
	)
	for row in rows:
		row["status_color"] = "blue"
	return rows


def get_service_records(case_name: str) -> list[dict]:
	records = frappe.get_all(
		"Service Record",
		filters={"legal_case": case_name},
		fields=[
			"name",
			"title",
			"status",
			"opening_date",
			"pending_total",
			"billed_total",
			"grand_total",
		],
		order_by="modified desc",
		limit=HUB_LIMIT_SMALL,
	)
	if not records:
		return []

	names = [row.name for row in records]
	act = frappe.qb.DocType("Legal Act Item")
	acts = (
		frappe.qb.from_(act)
		.select(
			act.parent,
			Count(act.name).as_("act_count"),
		)
		.where(act.parent.isin(names))
		.groupby(act.parent)
	).run(as_dict=True)
	act_map = {row.parent: row.act_count for row in acts}

	for row in records:
		row["act_count"] = int(act_map.get(row.name, 0))
		row["status_color"] = _status_color(row.status)
	return records


def get_time_entries(case_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Time Entry",
		filters={"legal_case": case_name},
		fields=[
			"name",
			"title",
			"activity",
			"entry_date",
			"duration_hours",
			"duration_minutes",
			"billable",
			"responsible",
		],
		order_by="entry_date desc",
		limit=HUB_LIMIT,
	)
	total_hours = 0.0
	for row in rows:
		hours = flt(row.duration_hours)
		if not hours and row.duration_minutes:
			hours = flt(row.duration_minutes) / 60.0
		row["hours"] = round(hours, 2)
		total_hours += hours
	return {"items": rows, "total_hours": round(total_hours, 2)}


def get_document_kits(case_name: str) -> list[dict]:
	_ = case_name
	return frappe.get_all(
		"Document Kit",
		filters={"enabled": 1},
		fields=["name", "title", "description"],
		order_by="title asc",
		limit=HUB_LIMIT,
	)


def get_case_documents(case_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Case Document",
		filters={"legal_case": case_name},
		fields=[
			"name",
			"title",
			"category",
			"status",
			"source",
			"version_label",
			"file",
			"creation",
		],
		order_by="creation desc",
		limit=HUB_LIMIT_SMALL,
	)
	for row in rows:
		row["status_color"] = _status_color(row.status)
	return rows


def get_financial(case_name: str) -> dict:
	agreement = frappe.db.get_value(
		"Fee Agreement",
		{"legal_case": case_name, "docstatus": ["!=", 2]},
		[
			"name",
			"title",
			"fee_mode",
			"status",
			"total_agreement_value",
			"lawyer_total",
			"client_total",
			"installment_count",
		],
		as_dict=True,
	)

	inst = frappe.qb.DocType("Fee Installment")
	agr = frappe.qb.DocType("Fee Agreement")
	installments = (
		frappe.qb.from_(inst)
		.join(agr)
		.on(inst.parent == agr.name)
		.select(
			inst.name,
			inst.due_date,
			inst.total_amount,
			inst.lawyer_amount,
			inst.client_amount,
			inst.status,
			inst.idx,
			agr.name.as_("fee_agreement"),
			agr.title.as_("fee_agreement_title"),
		)
		.where(agr.legal_case == case_name)
		.orderby(inst.due_date)
		.limit(HUB_LIMIT)
	).run(as_dict=True)

	payments = frappe.get_all(
		"Legal Payment",
		filters={"legal_case": case_name},
		fields=[
			"name",
			"title",
			"amount",
			"received_amount",
			"due_date",
			"received_date",
			"status",
			"origin_type",
		],
		order_by="due_date desc",
		limit=HUB_LIMIT,
	)

	court_costs = frappe.get_all(
		"Court Cost",
		filters={"legal_case": case_name},
		fields=["name", "title", "description", "amount", "type", "payment_date", "status"],
		order_by="payment_date desc",
		limit=HUB_LIMIT,
	)

	for row in installments + payments + court_costs:
		row["status_color"] = _status_color(row.get("status"))

	total_contract = flt(agreement.total_agreement_value if agreement else 0)
	total_received = sum(
		flt(p.received_amount or p.amount)
		for p in payments
		if p.status in RECEIVED_PAYMENT_STATUSES
	)
	total_pending = sum(flt(p.amount) for p in payments if p.status in ("Pendente", "Vencido"))
	total_costs = sum(flt(c.amount) for c in court_costs)

	return {
		"agreement": agreement,
		"installments": installments,
		"payments": payments,
		"court_costs": court_costs,
		"summary": {
			"total_contract": total_contract,
			"total_received": total_received,
			"total_pending": total_pending,
			"total_costs": total_costs,
			"net_margin": total_received - total_costs,
		},
	}
