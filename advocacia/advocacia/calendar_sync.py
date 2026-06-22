import frappe
from frappe.utils import add_to_date, get_datetime


def sync_audiencia_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de uma Audiência."""
	if doc.status == "Cancelada":
		_cancel_linked_event(doc)
		return

	event_name = _find_linked_event("Hearing", doc.name)
	starts_on = get_datetime(doc.hearing_datetime)
	ends_on = add_to_date(starts_on, hours=2)

	event_data = {
		"subject": _audiencia_subject(doc),
		"starts_on": starts_on,
		"ends_on": ends_on,
		"event_type": "Public",
		"description": _audiencia_description(doc),
		"custom_source_doctype": "Hearing",
		"custom_source_name": doc.name,
	}

	_save_or_create_event(event_name, event_data)


def sync_prazo_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de um Prazo."""
	if doc.status == "Concluído":
		_cancel_linked_event(doc)
		return

	source_dt = "Deadline"
	event_name = _find_linked_event(source_dt, doc.name)

	event_data = {
		"subject": f"PRAZO: {doc.description}",
		"starts_on": doc.due_date,
		"all_day": 1,
		"event_type": "Public",
		"description": _prazo_description(doc),
		"color": _prazo_color(doc.priority),
		"custom_source_doctype": source_dt,
		"custom_source_name": doc.name,
	}

	_save_or_create_event(event_name, event_data)


def _find_linked_event(source_doctype, source_name):
	return frappe.db.get_value(
		"Event",
		{"custom_source_doctype": source_doctype, "custom_source_name": source_name},
	)


def _save_or_create_event(event_name, event_data):
	if event_name:
		event = frappe.get_doc("Event", event_name)
		event.update(event_data)
		event.save(ignore_permissions=True)  # sistema sincroniza Event em nome do usuário
	else:
		event = frappe.get_doc({"doctype": "Event", **event_data})
		event.insert(ignore_permissions=True)  # sistema sincroniza Event em nome do usuário


def _cancel_linked_event(doc):
	event_name = _find_linked_event(doc.doctype, doc.name)
	if event_name:
		frappe.db.set_value("Event", event_name, "status", "Closed")


def _prazo_color(prioridade):
	if prioridade == "Alta":
		return "red"
	if prioridade == "Média":
		return "orange"
	return "blue"


def _audiencia_subject(doc):
	cliente = frappe.db.get_value("Legal Case", doc.legal_case, "client") if doc.legal_case else ""
	return f"Audiência {doc.type}: {cliente}"


def _audiencia_description(doc):
	parts = [f"Tipo: {doc.type}", f"Processo: {doc.legal_case}"]
	if doc.modality == "Virtual" and doc.link_virtual:
		parts.append(f"Link: {doc.link_virtual}")
	if doc.court_branch:
		parts.append(f"Vara: {doc.court_branch}")
	if doc.remarks:
		parts.append(f"Obs: {doc.remarks}")
	return "\n".join(parts)


def _prazo_description(doc):
	parts = [f"Processo: {doc.legal_case}", f"Prioridade: {doc.priority or 'Normal'}"]
	if doc.responsible:
		parts.append(f"Responsável: {doc.responsible}")
	if doc.remarks:
		parts.append(f"Obs: {doc.remarks}")
	return "\n".join(parts)
