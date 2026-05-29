import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from advocacia.advocacia.validators import limpar_numerico, validar_cnj


class Servico(Document):
	def before_save(self):
		if self.tipo != "Processo Judicial":
			self.numeracao_legada = 0

	def validate(self):
		if self.tipo != "Processo Judicial":
			return

		legado = cint(self.numeracao_legada)
		numero = (self.numero_processo or "").strip()

		if not legado:
			if not numero:
				frappe.throw(
					_("Informe o número do processo no formato CNJ."),
					title=_("Campo obrigatório"),
				)
			self.numero_processo = validar_cnj(numero)
			self.numero_processo = limpar_numerico(self.numero_processo)
		elif numero:
			self.numero_processo = numero


def format_servico_link_label(doc=None, servico_name=None):
	"""Rótulo legível para links e autocomplete de Serviço."""
	if doc is None:
		doc = frappe.get_cached_doc("Servico", servico_name)
	elif not hasattr(doc, "get"):
		doc = frappe._dict(doc)

	title = (doc.get("title") or doc.get("name") or "").strip()
	parts = [title] if title else []

	cliente = doc.get("cliente")
	if cliente:
		cliente_nome = frappe.db.get_value("Cliente", cliente, "nome") or cliente
		if cliente_nome and cliente_nome not in parts:
			parts.append(cliente_nome)

	numero_processo = doc.get("numero_processo") or ""
	if numero_processo:
		if cint(doc.get("numeracao_legada")):
			if numero_processo not in parts:
				parts.append(numero_processo)
		else:
			digits = "".join(ch for ch in str(numero_processo) if ch.isdigit())
			if len(digits) == 20:
				numero_processo = (
					f"{digits[:7]}-{digits[7:9]}.{digits[9:13]}."
					f"{digits[13]}.{digits[14:16]}.{digits[16:]}"
				)
			if numero_processo not in parts:
				parts.append(numero_processo)

	status = doc.get("status")
	if status and status not in parts:
		parts.append(status)

	return " · ".join(parts) if parts else doc.get("name") or servico_name or ""


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def servico_query(doctype, txt, searchfield, start, page_len, filters):
	txt = (txt or "").strip()
	list_filters = dict(filters or {})

	or_filters = [
		["name", "like", f"%{txt}%"],
		["title", "like", f"%{txt}%"],
		["cliente", "like", f"%{txt}%"],
		["numero_processo", "like", f"%{txt}%"],
		["status", "like", f"%{txt}%"],
	]

	if txt:
		clientes = frappe.get_all(
			"Cliente",
			filters={"nome": ["like", f"%{txt}%"]},
			pluck="name",
			limit_page_length=50,
		)
		if clientes:
			or_filters.append(["cliente", "in", clientes])

	rows = frappe.get_all(
		"Servico",
		filters=list_filters,
		or_filters=or_filters if txt else None,
		fields=["name", "title", "cliente", "numero_processo", "status", "numeracao_legada"],
		limit_start=start,
		limit_page_length=page_len,
		order_by="modified desc",
	)

	return [(row.name, format_servico_link_label(doc=row)) for row in rows]


@frappe.whitelist()
def get_link_title(doctype, docname):
	if doctype == "Servico":
		return format_servico_link_label(servico_name=docname)

	from frappe.desk.search import get_link_title as frappe_get_link_title

	return frappe_get_link_title(doctype, docname)
