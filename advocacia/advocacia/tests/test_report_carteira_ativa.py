import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.report.carteira_ativa.carteira_ativa import execute
from advocacia.advocacia.tests.test_setup import create_test_servico, _uid


class TestReportCarteiraAtiva(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_execute_lista_servico_em_andamento(self):
		titulo = _uid("Serviço Carteira")
		servico = create_test_servico(
			tipo="Consultoria",
			status="Em andamento",
			title=titulo,
			area="Cível",
		)

		columns, data, _msg, _chart, _summary = execute({"area": "Cível"})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		row = next((r for r in data if r.get("servico") == servico.name), None)
		self.assertIsNotNone(row)
		self.assertEqual(row.get("cliente"), servico.cliente)

	def test_execute_filtro_cliente(self):
		servico = create_test_servico(status="Em andamento")
		columns, data, _msg, _chart, _summary = execute({"cliente": servico.cliente})
		self.assertTrue(columns)
		self.assertTrue(any(r.get("servico") == servico.name for r in data))
