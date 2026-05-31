import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.painel_api import get_painel_data, marcar_parcela_recebida
from advocacia.advocacia.tests.test_setup import create_test_acordo, get_acordo_pagamentos


class TestPainelApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_painel_data_estrutura(self):
		data = get_painel_data()
		for key in (
			"kpis",
			"resumo",
			"financeiro",
			"alertas",
			"parcelas",
			"despesas_pendentes",
			"total_despesas_mes",
			"audiencias",
			"prazos",
			"tarefas",
		):
			self.assertIn(key, data)

	def test_get_painel_data_sem_erro_vazio(self):
		data = get_painel_data(limit_page_length=5)
		self.assertIsInstance(data["parcelas"], list)
		self.assertIsInstance(data["tarefas"], list)

	def test_marcar_parcela_recebida(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		result = marcar_parcela_recebida(pag_name)
		self.assertTrue(result.get("ok"))
		self.assertEqual(frappe.db.get_value("Pagamento", pag_name, "status"), "Recebido")

	def test_marcar_parcela_ja_recebida_falha(self):
		from frappe.exceptions import ValidationError

		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		marcar_parcela_recebida(pag_name)
		with self.assertRaises(ValidationError):
			marcar_parcela_recebida(pag_name)

	def test_paginacao(self):
		data_small = get_painel_data(limit_start=0, limit_page_length=1)
		data_large = get_painel_data(limit_start=0, limit_page_length=100)
		self.assertLessEqual(len(data_small["tarefas"]), 1)
		self.assertLessEqual(len(data_small["tarefas"]), len(data_large["tarefas"]))
