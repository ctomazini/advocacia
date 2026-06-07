"""Backfill idempotente de títulos vazios (setup / bench execute)."""

import frappe

from advocacia.advocacia.titulos import COMPOSTOS, aplicar_titulo_pos_insert


def ensure_backfill_titles(commit=False):
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

	if commit:
		frappe.db.commit()  # setup: backfill de títulos vazios

	frappe.logger().info("ensure_backfill_titles: %s registros atualizados", atualizados)
	return atualizados
