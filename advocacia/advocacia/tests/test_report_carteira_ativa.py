import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.report.carteira_ativa.carteira_ativa import execute
from advocacia.advocacia.tests.test_setup import create_test_legal_case, _uid


class TestReportCarteiraAtiva(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_lista_servico_em_andamento(self):
		titulo = _uid("Serviço Carteira")
		servico = create_test_legal_case(
			tipo="Consultoria",
			status="Em andamento",
			title=titulo,
			area="Cível",
		)

		columns, data, _msg, _chart, _summary = execute({"area": "Cível"})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		row = next((r for r in data if r.get("legal_case") == servico.name), None)
		self.assertIsNotNone(row)
		self.assertEqual(row.get("client"), servico.client)

	def test_execute_filtro_cliente(self):
		servico = create_test_legal_case(status="Em andamento")
		columns, data, _msg, _chart, _summary = execute({"client": servico.client})
		self.assertTrue(columns)
		self.assertTrue(any(r.get("legal_case") == servico.name for r in data))
