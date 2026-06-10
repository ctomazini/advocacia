"""Processos ativos enriquecidos para o painel."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import getdate, today

from advocacia.advocacia.painel._helpers import _cliente_nome_lookup

ACTIVE_CASE_STATUSES = ("Em andamento",)


def get_active_cases_enriched(limit: int) -> list[dict]:
	hoje = getdate(today())
	cases = frappe.get_all(
		"Legal Case",
		filters={"status": ["in", list(ACTIVE_CASE_STATUSES)]},
		fields=["name", "title", "client", "status", "case_phase", "type", "case_number"],
		order_by="modified desc",
		limit=limit,
	)
	if not cases:
		return []

	case_names = [row.name for row in cases]
	client_map = _cliente_nome_lookup([row.client for row in cases if row.client])

	deadlines = frappe.get_all(
		"Deadline",
		filters={"legal_case": ["in", case_names], "status": "Pendente"},
		fields=["legal_case", "title", "description", "due_date"],
		order_by="due_date asc",
		limit=500,
	)
	next_deadline: dict[str, dict] = {}
	for row in deadlines:
		if row.legal_case not in next_deadline:
			next_deadline[row.legal_case] = row

	hearings = frappe.get_all(
		"Hearing",
		filters={
			"legal_case": ["in", case_names],
			"status": ["in", ["Agendada", "Adiada"]],
		},
		fields=["legal_case", "title", "hearing_datetime", "type"],
		order_by="hearing_datetime asc",
		limit=500,
	)
	next_hearing: dict[str, dict] = {}
	for row in hearings:
		if row.legal_case not in next_hearing:
			next_hearing[row.legal_case] = row

	result = []
	for case in cases:
		dl = next_deadline.get(case.name)
		hg = next_hearing.get(case.name)
		next_label = ""
		next_date = None
		next_overdue = False
		next_kind = ""

		candidates = []
		if dl and dl.due_date:
			candidates.append(
				(
					getdate(dl.due_date),
					"prazo",
					dl.title or dl.description or dl.name,
					getdate(dl.due_date) < hoje,
				)
			)
		if hg and hg.hearing_datetime:
			hg_date = getdate(hg.hearing_datetime)
			candidates.append(
				(
					hg_date,
					"audiencia",
					hg.title or hg.type or hg.name,
					hg_date < hoje,
				)
			)

		if candidates:
			candidates.sort(key=lambda item: item[0])
			next_date, next_kind, next_label, next_overdue = candidates[0]
			prefix = _("Prazo") if next_kind == "prazo" else _("Audiência")
			next_label = f"{prefix}: {next_label}"

		result.append(
			{
				"name": case.name,
				"title": case.title or case.name,
				"client_name": client_map.get(case.client) or case.client or "",
				"status": case.status,
				"case_phase": case.case_phase or "",
				"type": case.type or "",
				"case_number": case.case_number or "",
				"next_event_label": next_label,
				"next_event_date": next_date,
				"next_event_overdue": next_overdue,
			}
		)

	return result
