import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.report.fluxo_de_caixa.fluxo_de_caixa import execute
from advocacia.advocacia.tests.test_setup import create_test_legal_payment


class TestReportFluxoDeCaixa(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_retorna_entrada_recebida(self):
		pag = create_test_legal_payment(amount=2500, status="Recebido")
		frappe.db.set_value(
			"Legal Payment",
			pag.name,
			{"received_date": today(), "received_amount": 2500},
			update_modified=False,
		)

		columns, data, _msg, _chart, _summary = execute({"meses": 6})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		entrada_rows = [r for r in data if r.get("documento") == pag.name]
		self.assertGreaterEqual(len(entrada_rows), 1)
		self.assertGreaterEqual(entrada_rows[0].get("valor_entrada", 0), 2500)

	def test_execute_sem_filtro_cliente(self):
		columns, data, _msg, _chart, _summary = execute({})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
