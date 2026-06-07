import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.report.honorarios_por_cliente.honorarios_por_cliente import execute
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_client,
	create_test_legal_case,
	get_acordo_pagamentos,
)


class TestReportHonorariosPorClient(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_agrega_por_cliente(self):
		cliente = create_test_client()
		servico = create_test_legal_case(cliente=cliente.name)
		acordo = create_test_acordo(
			servico=servico.name, valor_total=5000, num_parcelas=2
		)
		pagamentos = get_acordo_pagamentos(acordo.name)
		pendente = pagamentos[0]
		recebido = pagamentos[1]
		frappe.db.set_value(
			"Legal Payment",
			pendente.name,
			{"status": "Pendente", "data_vencimento": add_days(today(), 10), "valor": 3000},
			update_modified=False,
		)
		frappe.db.set_value(
			"Legal Payment",
			recebido.name,
			{
				"status": "Recebido",
				"data_vencimento": add_days(today(), -1),
				"data_recebimento": today(),
				"valor": 2000,
				"valor_recebido": 2000,
			},
			update_modified=False,
		)

		columns, data, _msg, _chart, _summary = execute(
			{
				"client": cliente.name,
				"de_data": add_days(today(), -30),
				"ate_data": add_days(today(), 30),
			}
		)
		self.assertTrue(columns)
		self.assertGreaterEqual(len(data), 1)
		row = next((r for r in data if r.get("client") == cliente.name), None)
		self.assertIsNotNone(row)
		self.assertGreaterEqual(row.get("total_contratado", 0), 5000)

	def test_execute_vazio_fora_periodo(self):
		columns, data, _msg, _chart, _summary = execute(
			{"de_data": "2099-01-01", "ate_data": "2099-06-30"}
		)
		self.assertTrue(columns)
		self.assertEqual(data, [])
