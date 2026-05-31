import frappe
from frappe.utils import add_to_date, get_datetime


def sync_audiencia_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de uma Audiência."""
	if doc.status_aud == "Cancelada":
		_cancel_linked_event(doc)
		return

	event_name = _find_linked_event("Audiencia", doc.name)
	starts_on = get_datetime(doc.data_hora)
	ends_on = add_to_date(starts_on, hours=2)

	event_data = {
		"subject": _audiencia_subject(doc),
		"starts_on": starts_on,
		"ends_on": ends_on,
		"event_type": "Public",
		"description": _audiencia_description(doc),
		"custom_source_doctype": "Audiencia",
		"custom_source_name": doc.name,
	}

	_save_or_create_event(event_name, event_data)


def sync_prazo_to_event(doc, method=None):
	"""Cria/atualiza Event do Frappe a partir de um Prazo."""
	if doc.status == "Concluído":
		_cancel_linked_event(doc)
		return

	source_dt = "Controle de Prazos"
	event_name = _find_linked_event(source_dt, doc.name)

	event_data = {
		"subject": f"PRAZO: {doc.descricao}",
		"starts_on": doc.data_prazo,
		"all_day": 1,
		"event_type": "Public",
		"description": _prazo_description(doc),
		"color": _prazo_color(doc.prioridade),
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
		event.save(ignore_permissions=True)
	else:
		event = frappe.get_doc({"doctype": "Event", **event_data})
		event.insert(ignore_permissions=True)


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
	cliente = frappe.db.get_value("Servico", doc.servico, "cliente") if doc.servico else ""
	return f"Audiência {doc.tipo}: {cliente}"


def _audiencia_description(doc):
	parts = [f"Tipo: {doc.tipo}", f"Serviço: {doc.servico}"]
	if doc.modalidade == "Virtual" and doc.link_virtual:
		parts.append(f"Link: {doc.link_virtual}")
	if doc.local_vara:
		parts.append(f"Vara: {doc.local_vara}")
	if doc.observacoes:
		parts.append(f"Obs: {doc.observacoes}")
	return "\n".join(parts)


def _prazo_description(doc):
	parts = [f"Serviço: {doc.servico}", f"Prioridade: {doc.prioridade or 'Normal'}"]
	if doc.responsavel:
		parts.append(f"Responsável: {doc.responsavel}")
	if doc.observacoes:
		parts.append(f"Obs: {doc.observacoes}")
	return "\n".join(parts)
