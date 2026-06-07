import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.report.horas_por_servico.horas_por_servico import execute as horas_execute
from advocacia.advocacia.report.produtividade.produtividade import execute as prod_execute
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_court_cost,
	create_test_registro_horas,
	create_test_legal_case,
)


class TestReportProdutividade(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_produtividade_executa_sem_erro_vazio(self):
		columns, data, _msg, _chart, _summary = prod_execute({"periodo": "Tudo"})
		self.assertTrue(columns)
		self.assertIsInstance(data, list)
		self.assertIsInstance(_summary, list)

	def test_produtividade_com_dados(self):
		servico = create_test_legal_case(area="Cível", status="Encerrado")
		create_test_acordo(servico=servico.name, valor_total=10000)
		create_test_court_cost(servico=servico.name, valor=500, status="Pago", data_pagamento=frappe.utils.today())
		create_test_registro_horas(servico=servico.name, duracao_minutos=120)

		columns, data, _msg, _chart, _summary = prod_execute({"periodo": "Tudo", "incluir_horas": 1})
		civil = next((r for r in data if r.get("area") == "Cível"), None)
		self.assertIsNotNone(civil)
		self.assertGreaterEqual(civil.get("total_honorarios", 0), 10000)
		self.assertGreaterEqual(civil.get("total_custas", 0), 500)
		self.assertGreaterEqual(civil.get("horas_registradas", 0), 2)
		self.assertGreaterEqual(len(_summary), 4)

	def test_horas_por_servico_executa(self):
		servico = create_test_legal_case()
		create_test_registro_horas(servico=servico.name, duracao_minutos=60, cobravel=1)
		create_test_registro_horas(servico=servico.name, duracao_minutos=30, cobravel=0)

		columns, data, _msg, chart, summary = horas_execute(
			{"legal_case": servico.name, "periodo": "Tudo"}
		)
		data_rows = [r for r in data if r.get("legal_case")]
		self.assertEqual(len(data_rows), 1)
		self.assertEqual(data_rows[0]["total_horas"], 1.5)
		self.assertEqual(data_rows[0]["horas_cobraveis"], 1.0)
		self.assertEqual(data_rows[0]["horas_nao_cobraveis"], 0.5)
		self.assertIsNotNone(chart)
		self.assertGreaterEqual(len(summary), 4)

	def test_horas_por_servico_vazio(self):
		columns, data, _msg, chart, summary = horas_execute({"periodo": "Tudo"})
		self.assertIsInstance(data, list)
		self.assertIsInstance(summary, list)
