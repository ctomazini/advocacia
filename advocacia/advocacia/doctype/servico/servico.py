import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from advocacia.advocacia.titulos import (
	aplicar_titulo_pos_insert,
	get_cliente_nome,
	join_title_parts,
	recompor_titulo_se_vazio,
)
from advocacia.advocacia.validators import limpar_numerico, validar_cnj


class Servico(Document):
	def before_save(self):
		if self.tipo != "Processo Judicial":
			self.numeracao_legada = 0

	def validate(self):
		if self.tipo != "Processo Judicial":
			recompor_titulo_se_vazio(self)
			return

		legado = cint(self.numeracao_legada)
		numero = (self.numero_processo or "").strip()

		if not numero:
			self.numero_processo = None
		elif not legado:
			self.numero_processo = limpar_numerico(validar_cnj(numero))
		else:
			self.numero_processo = numero
		recompor_titulo_se_vazio(self)

	def after_insert(self):
		aplicar_titulo_pos_insert(self)


def format_servico_link_label(doc=None, servico_name=None):
	"""Rótulo secundário para autocomplete de Serviço."""
	if doc is None:
		doc = frappe.get_cached_doc("Servico", servico_name)
	elif not hasattr(doc, "get"):
		doc = frappe._dict(doc)

	title = (doc.get("title") or "").strip()
	if title:
		return title

	cliente_nome = get_cliente_nome(doc.get("cliente"))
	name = doc.get("name") or servico_name or ""
	if name and cliente_nome:
		return join_title_parts(name, cliente_nome)
	return cliente_nome or name


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
