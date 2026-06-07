import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.painel_api import get_painel_data, marcar_parcela_recebida
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_hearing,
	create_test_legal_case,
	get_acordo_pagamentos,
)


class TestPainelApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_painel_data_estrutura(self):
		data = get_painel_data()
		for key in (
			"periodo_dias",
			"list_limit",
			"list_limits",
			"list_meta",
			"kpis",
			"resumo",
			"financeiro",
			"alertas",
			"centro_atencao",
			"timeline",
			"fee_installments",
			"despesas_pendentes",
			"total_despesas_mes",
			"custas_pendentes_repasse",
			"total_custas_mes",
			"comunicacoes_pendentes",
			"ultimas_comunicacoes",
			"horas_semana",
			"horas_periodo",
			"audiencias",
			"prazos",
			"tarefas",
		):
			self.assertIn(key, data)

	def test_get_painel_data_sem_erro_vazio(self):
		data = get_painel_data(limit_page_length=5)
		self.assertIsInstance(data["fee_installments"], list)
		self.assertIsInstance(data["tarefas"], list)

	def test_marcar_parcela_recebida(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		result = marcar_parcela_recebida(pag_name)
		self.assertTrue(result.get("ok"))
		self.assertEqual(frappe.db.get_value("Legal Payment", pag_name, "status"), "Recebido")

	def test_marcar_parcela_ja_recebida_falha(self):
		from frappe.exceptions import ValidationError

		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		marcar_parcela_recebida(pag_name)
		with self.assertRaises(ValidationError):
			marcar_parcela_recebida(pag_name)

	def test_paginacao(self):
		data_small = get_painel_data(limit_start=0, limit_page_length=1, list_limit=5)
		data_large = get_painel_data(
			limit_start=0,
			limit_page_length=100,
			list_limits={"timeline": 0, "fee_installments": 0, "despesas": 0, "custas": 0, "comunicacoes": 0},
		)
		self.assertLessEqual(len(data_small["tarefas"]), 5)
		self.assertLessEqual(len(data_small["tarefas"]), len(data_large["tarefas"]))

	def test_periodo_dias(self):
		data = get_painel_data(periodo_dias=30)
		self.assertEqual(data["periodo_dias"], 30)
		self.assertIsInstance(data["timeline"], list)
		self.assertIn("audiencias_amanha", data["kpis"])

	def test_list_limit(self):
		data = get_painel_data(list_limit=5)
		self.assertEqual(data["list_limit"], 5)
		self.assertEqual(data["list_limits"]["timeline"], 5)
		self.assertIn("timeline", data["list_meta"])
		self.assertLessEqual(data["list_meta"]["timeline"]["showing"], 5)
		data_all = get_painel_data(list_limit=0)
		self.assertEqual(data_all["list_limit"], 0)

	def test_list_limits_independentes(self):
		data = get_painel_data(
			list_limits={
				"timeline": 5,
				"comunicacoes": 10,
				"fee_installments": 15,
				"despesas": 0,
				"custas": 5,
			}
		)
		self.assertEqual(data["list_limits"]["timeline"], 5)
		self.assertEqual(data["list_limits"]["comunicacoes"], 10)
		self.assertEqual(data["list_limits"]["fee_installments"], 15)
		self.assertEqual(data["list_limits"]["despesas"], 0)
		self.assertLessEqual(data["list_meta"]["timeline"]["showing"], 5)
		self.assertLessEqual(data["list_meta"]["comunicacoes"]["showing"], 10)
		self.assertLessEqual(data["list_meta"]["fee_installments"]["showing"], 15)
		if data["list_meta"]["despesas"]["total"]:
			self.assertEqual(
				data["list_meta"]["despesas"]["showing"],
				data["list_meta"]["despesas"]["total"],
			)

	def test_hearings_incluem_servico_titulo(self):
		servico = create_test_legal_case()
		create_test_hearing(servico=servico.name)
		data = get_painel_data(periodo_dias=30)
		audiencias = [a for a in data["audiencias"] if a.get("legal_case") == servico.name]
		self.assertTrue(audiencias, "audiência de teste deve aparecer no painel")
		self.assertTrue(
			audiencias[0].get("servico_titulo"),
			"servico_titulo deve vir preenchido (não só o ID)",
		)
		self.assertIn(servico.name, audiencias[0]["servico_titulo"])
