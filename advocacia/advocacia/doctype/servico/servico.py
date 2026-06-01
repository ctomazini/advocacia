import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from advocacia.advocacia.titulos import get_cliente_nome, join_title_parts
from advocacia.advocacia.validators import limpar_numerico, validar_cnj


class Servico(Document):
	def before_save(self):
		if self.tipo != "Processo Judicial":
			self.numeracao_legada = 0

	def validate(self):
		self._compor_titulo()
		if self.tipo != "Processo Judicial":
			return

		legado = cint(self.numeracao_legada)
		numero = (self.numero_processo or "").strip()

		if not numero:
			self.numero_processo = None
		elif not legado:
			self.numero_processo = limpar_numerico(validar_cnj(numero))
		else:
			self.numero_processo = numero

	def _compor_titulo(self):
		if self.title:
			return
		partes = []
		cliente_nome = get_cliente_nome(self.cliente)
		if cliente_nome:
			partes.append(cliente_nome)
		if self.tipo:
			partes.append(self.tipo)
		if self.numero_processo:
			partes.append(self.numero_processo)
		self.title = join_title_parts(*partes)


def format_servico_link_label(doc=None, servico_name=None):
	"""Rótulo legível para links e autocomplete de Serviço."""
	if doc is None:
		doc = frappe.get_cached_doc("Servico", servico_name)
	elif not hasattr(doc, "get"):
		doc = frappe._dict(doc)

	title = (doc.get("title") or "").strip()
	if title:
		return title

	partes = []
	cliente_nome = get_cliente_nome(doc.get("cliente"))
	if cliente_nome:
		partes.append(cliente_nome)
	if doc.get("tipo"):
		partes.append(doc.get("tipo"))

	numero_processo = doc.get("numero_processo") or ""
	if numero_processo:
		if not cint(doc.get("numeracao_legada")):
			digits = "".join(ch for ch in str(numero_processo) if ch.isdigit())
			if len(digits) == 20:
				numero_processo = (
					f"{digits[:7]}-{digits[7:9]}.{digits[9:13]}."
					f"{digits[13]}.{digits[14:16]}.{digits[16:]}"
				)
		partes.append(numero_processo)

	return join_title_parts(*partes) if partes else (doc.get("name") or servico_name or "")


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

