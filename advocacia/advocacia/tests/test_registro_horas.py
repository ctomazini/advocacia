import frappe
from frappe.exceptions import MandatoryError
from frappe.tests.utils import FrappeTestCase

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
