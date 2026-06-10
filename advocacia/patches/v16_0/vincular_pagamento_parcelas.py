import frappe

from advocacia.advocacia.financeiro import _vincular_pagamento_na_parcela


def execute():
	"""Preenche Link pagamento nas parcelas existentes (backfill idempotente)."""
	parcelas = frappe.get_all(
		"Fee Installment",
		filters={"installment_origin_id": ["is", "set"]},
		fields=["installment_origin_id", "payment"],
	)
	vinculados = 0
	for row in parcelas:
		if row.payment:
			continue
		pagamento_name = frappe.db.get_value(
			"Legal Payment", {"installment_origin_id": row.installment_origin_id}, "name"
		)
		if pagamento_name:
			_vincular_pagamento_na_parcela(row.installment_origin_id, pagamento_name)
			vinculados += 1

	frappe.db.commit()
	frappe.logger().info(
		"Backfill pagamento em parcelas: {0} vínculos criados".format(vinculados)
	)
