"""Helpers para títulos no formato `{ID} — {descritor}`."""

import frappe

TITLE_SEPARATOR = " — "

COMPOSTOS = {
	"Servico": False,
	"Acordo de Honorarios Processuais": False,
	"Registro de Atos": False,
	"Pagamento": False,
	"Audiencia": False,
	"Controle de Prazos": False,
	"Tarefa": False,
	"Comunicacao": False,
	"Registro de Horas": False,
	"Custa Processual": False,
	"Despesa do Escritorio": True,
}


def get_cliente_nome(cliente):
	if not cliente:
		return ""
	return frappe.db.get_value("Cliente", cliente, "nome") or cliente


def join_title_parts(*parts):
	cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
	return TITLE_SEPARATOR.join(cleaned)


def _resolver_descritor(doc, usar_descricao=False):
	if not usar_descricao and getattr(doc, "cliente", None):
		descritor = get_cliente_nome(doc.cliente)
		if descritor:
			return descritor
	descritor = (getattr(doc, "descricao", None) or "").strip()
	if descritor:
		return descritor
	return doc.doctype


def aplicar_titulo_pos_insert(doc, usar_descricao=False):
	"""Preenche title após insert quando ainda vazio."""
	if doc.title:
		return
	if not doc.name or str(doc.name).startswith("new-"):
		return
	descritor = _resolver_descritor(doc, usar_descricao=usar_descricao)
	novo = join_title_parts(doc.name, descritor)
	if novo:
		doc.db_set("title", novo, update_modified=False)
		doc.title = novo


def recompor_titulo_se_vazio(doc, usar_descricao=False):
	"""Recompõe title em re-save se usuário limpou o campo."""
	if doc.title:
		return
	if doc.is_new() or not doc.name or str(doc.name).startswith("new-"):
		return
	aplicar_titulo_pos_insert(doc, usar_descricao=usar_descricao)


def backfill_titulos_vazios():
	"""Recompõe apenas registros com title vazio (conservador)."""
	atualizados = 0
	for dt, usar_descricao in COMPOSTOS.items():
		for row in frappe.get_all(dt, fields=["name", "title"]):
			if row.get("title"):
				continue
			doc = frappe.get_doc(dt, row.name)
			aplicar_titulo_pos_insert(doc, usar_descricao=usar_descricao)
			if frappe.db.get_value(dt, row.name, "title"):
				atualizados += 1
	frappe.db.commit()
	frappe.logger().info("backfill_titulos_vazios: %s registros atualizados", atualizados)
	return atualizados
