import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.report.inadimplencia.inadimplencia import execute
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_client,
	create_test_legal_case,
	get_acordo_pagamentos,
)


class TestReportInadimplencia(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_retorna_colunas_e_dados(self):
		cliente = create_test_client()
		servico = create_test_legal_case(cliente=cliente.name)
		acordo = create_test_acordo(servico=servico.name, total_amount=1500, num_parcelas=1)
		pag = get_acordo_pagamentos(acordo.name)[0]
		frappe.db.set_value(
			"Legal Payment",
			pag.name,
			{
				"status": "Vencido",
				"due_date": add_days(today(), -5),
				"manual_override": 0,
			},
			update_modified=False,
		)

		columns, data, _msg, _chart, _summary = execute(
			{
				"de_data": add_days(today(), -30),
				"ate_data": today(),
				"client": cliente.name,
			}
		)
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		row = next((r for r in data if r.get("client") == cliente.name), None)
		self.assertIsNotNone(row)
		self.assertGreaterEqual(row.get("total_vencido", 0), 1500)
		self.assertGreaterEqual(row.get("qtd_parcelas", 0), 1)

	def test_execute_sem_dados_retorna_lista_vazia(self):
		columns, data, _msg, _chart, _summary = execute(
			{
				"de_data": "2099-01-01",
				"ate_data": "2099-12-31",
			}
		)
		self.assertTrue(columns)
		self.assertEqual(data, [])
