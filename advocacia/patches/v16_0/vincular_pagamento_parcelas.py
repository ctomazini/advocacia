import frappe

from advocacia.advocacia.financeiro import _vincular_pagamento_na_parcela


def execute():
	"""Preenche Link pagamento nas parcelas existentes (backfill idempotente)."""
	parcelas = frappe.get_all(
		"Fee Installment",
		filters={"parcela_origem_id": ["is", "set"]},
		fields=["parcela_origem_id", "payment"],
	)
	vinculados = 0
	for row in parcelas:
		if row.payment:
			continue
		pagamento_name = frappe.db.get_value(
			"Legal Payment", {"parcela_origem_id": row.parcela_origem_id}, "name"
		)
		if pagamento_name:
			_vincular_pagamento_na_parcela(row.parcela_origem_id, pagamento_name)
			vinculados += 1

	frappe.db.commit()
	frappe.logger().info(
		"Backfill pagamento em parcelas: {0} vínculos criados".format(vinculados)
	)
