import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today

from advocacia.advocacia.painel import get as get_painel_payload
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
			"is_manager",
			"kpis",
			"summary",
			"atencao",
			"proximo_evento",
			"timeline",
			"active_cases",
			"comunicacoes_pendentes",
			"ultimas_comunicacoes",
			"horas_semana",
			"horas_periodo",
		):
			self.assertIn(key, data)

		self.assertNotIn("agenda_dias", data)
		self.assertNotIn("alertas", data)
		self.assertNotIn("centro_atencao", data)

		if "Advocacia Manager" in frappe.get_roles():
			for key in (
				"financeiro",
				"saude_operacional",
				"fee_installments",
				"despesas_pendentes",
				"total_despesas_mes",
				"custas_pendentes_repasse",
				"total_custas_mes",
			):
				self.assertIn(key, data)
		else:
			self.assertNotIn("saude_operacional", data)
			self.assertNotIn("financeiro", data)

	def test_get_painel_data_sem_erro_vazio(self):
		data = get_painel_data(limit_page_length=5)
		self.assertIsInstance(data["timeline"], list)
		self.assertIsInstance(data["active_cases"], list)

	def test_marcar_parcela_recebida(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		result = marcar_parcela_recebida(pag_name)
		self.assertTrue(result.get("ok"))
		self.assertEqual(frappe.db.get_value("Legal Payment", pag_name, "status"), "Recebido")

	def test_marcar_parcela_ja_recebida_falha(self):
		from frappe.exceptions import ValidationError

		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		marcar_parcela_recebida(pag_name)
		with self.assertRaises(ValidationError):
			marcar_parcela_recebida(pag_name)

	def test_paginacao(self):
		data_small = get_painel_data(limit_start=0, limit_page_length=1, list_limit=5)
		data_large = get_painel_data(
			limit_start=0,
			limit_page_length=100,
			list_limits={
				"timeline": 0,
				"fee_installments": 0,
				"despesas": 0,
				"custas": 0,
				"comunicacoes": 0,
				"active_cases": 0,
			},
		)
		self.assertLessEqual(len(data_small["timeline"]), 5)
		self.assertLessEqual(len(data_small["timeline"]), len(data_large["timeline"]))

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
				"active_cases": 10,
			}
		)
		self.assertEqual(data["list_limits"]["timeline"], 5)
		self.assertEqual(data["list_limits"]["comunicacoes"], 10)
		self.assertEqual(data["list_limits"]["fee_installments"], 15)
		self.assertEqual(data["list_limits"]["active_cases"], 10)
		self.assertLessEqual(data["list_meta"]["timeline"]["showing"], 5)
		self.assertLessEqual(data["list_meta"]["comunicacoes"]["showing"], 10)
		self.assertLessEqual(data["list_meta"]["fee_installments"]["showing"], 15)
		self.assertLessEqual(data["list_meta"]["active_cases"]["showing"], 10)
		if data["list_meta"]["despesas"]["total"]:
			self.assertEqual(
				data["list_meta"]["despesas"]["showing"],
				data["list_meta"]["despesas"]["total"],
			)

	def test_hearings_incluem_servico_titulo_na_timeline(self):
		servico = create_test_legal_case()
		hearing = create_test_hearing(servico=servico.name)
		data = get_painel_data(periodo_dias=30)
		match = [row for row in data["timeline"] if row.get("docname") == hearing.name]
		self.assertTrue(match, "audiência de teste deve aparecer na timeline")
		self.assertEqual(match[0].get("type"), "audiencia")

	def test_active_cases_list_meta(self):
		create_test_legal_case(status="Em andamento")
		data = get_painel_data(list_limits={"active_cases": 5})
		self.assertIn("active_cases", data["list_meta"])
		self.assertGreaterEqual(data["list_meta"]["active_cases"]["total"], 1)

	def test_atencao_tile_audiencias_amanha(self):
		servico = create_test_legal_case()
		amanha = add_days(today(), 1)
		create_test_hearing(
			servico=servico.name,
			hearing_datetime=f"{amanha} 10:00:00",
		)
		data = get_painel_payload()
		labels = [tile.get("label") for tile in data["atencao"].get("tiles") or []]
		self.assertIn("Audiências amanhã", labels)

	def test_get_painel_data_sem_role_advocacia(self):
		user = "test_painel_no_role@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "No",
					"last_name": "Role",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_painel_data()
		finally:
			frappe.set_user("Administrator")
