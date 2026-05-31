import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from advocacia.advocacia.tests.test_setup import create_test_registro_horas, create_test_servico


class TestRegistroHoras(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud_valido(self):
		reg = create_test_registro_horas()
		self.assertTrue(reg.name)
		self.assertEqual(reg.duracao_horas, 1.0)

	def test_calculo_duracao_inicio_fim(self):
		reg = frappe.get_doc(
			{
				"doctype": "Registro de Horas",
				"servico": create_test_servico().name,
				"data": frappe.utils.today(),
				"atividade": "Pesquisa",
				"hora_inicio": "09:00:00",
				"hora_fim": "11:30:00",
			}
		)
		reg.insert(ignore_permissions=True)
		self.assertEqual(reg.duracao_minutos, 150)
		self.assertEqual(reg.duracao_horas, 2.5)

	def test_calculo_horas_de_minutos(self):
		reg = create_test_registro_horas(duracao_minutos=90)
		self.assertEqual(reg.duracao_horas, 1.5)

	def test_cliente_via_servico(self):
		servico = create_test_servico()
		cliente = frappe.db.get_value("Servico", servico.name, "cliente")
		reg = create_test_registro_horas(servico=servico.name)
		self.assertEqual(reg.cliente, cliente)

	def test_sem_servico_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Registro de Horas",
					"data": frappe.utils.today(),
					"atividade": "Teste",
					"duracao_minutos": 30,
				}
			).insert(ignore_permissions=True)

	def test_sem_atividade_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Registro de Horas",
					"servico": create_test_servico().name,
					"data": frappe.utils.today(),
					"duracao_minutos": 30,
				}
			).insert(ignore_permissions=True)

	def test_iniciar_timer(self):
		reg = create_test_registro_horas(duracao_minutos=30)
		result = reg.iniciar_timer()
		reg.reload()
		self.assertEqual(reg.timer_ativo, 1)
		self.assertTrue(reg.timer_inicio)
		self.assertIn("timer_inicio", result)

	def test_parar_timer_soma_duracao(self):
		reg = create_test_registro_horas(duracao_minutos=30)
		reg.iniciar_timer()
		frappe.db.set_value(
			"Registro de Horas",
			reg.name,
			"timer_inicio",
			add_to_date(now_datetime(), minutes=-10),
		)
		reg.reload()
		result = reg.parar_timer()
		reg.reload()
		self.assertEqual(reg.timer_ativo, 0)
		self.assertFalse(reg.timer_inicio)
		self.assertEqual(reg.duracao_minutos, 40)
		self.assertEqual(result["duracao_minutos"], 40)

	def test_iniciar_timer_duplicado_falha(self):
		reg = create_test_registro_horas()
		reg.iniciar_timer()
		reg.reload()
		with self.assertRaises(ValidationError):
			reg.iniciar_timer()

	def test_parar_timer_sem_ativo_falha(self):
		reg = create_test_registro_horas()
		with self.assertRaises(ValidationError):
			reg.parar_timer()

	def test_edicao_duracao_com_timer_ativo_falha(self):
		reg = create_test_registro_horas(duracao_minutos=30)
		reg.iniciar_timer()
		reg.reload()
		reg.duracao_minutos = 60
		with self.assertRaises(ValidationError):
			reg.save()
