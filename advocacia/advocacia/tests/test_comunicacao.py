import frappe
from frappe.exceptions import MandatoryError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	create_test_client,
	create_test_case_communication,
	create_test_legal_case,
)


class TestCaseCommunication(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud_valido(self):
		com = create_test_case_communication()
		self.assertTrue(com.name)

	def test_client_via_servico(self):
		servico = create_test_legal_case()
		cliente = frappe.db.get_value("Legal Case", servico.name, "client")
		com = frappe.get_doc(
			{
				"doctype": "Case Communication",
				"legal_case": servico.name,
				"subject": "Teste via serviço",
				"type": "Telefone",
				"communication_date": frappe.utils.now_datetime(),
			}
		)
		com.insert(ignore_permissions=True)
		self.assertEqual(com.client, cliente)

	def test_gerar_tarefa_automatica(self):
		com = create_test_case_communication(
			generate_task=1,
			next_steps="Retornar ligação amanhã",
		)
		com.reload()
		self.assertTrue(com.legal_task)
		tarefa = frappe.get_doc("Legal Task", com.legal_task)
		self.assertIn("Follow-up:", tarefa.subject)

	def test_sem_assunto_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Case Communication",
					"client": create_test_client().name,
					"type": "Telefone",
					"communication_date": frappe.utils.now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_sem_tipo_falha(self):
		from frappe.exceptions import ValidationError

		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Case Communication",
					"client": create_test_client().name,
					"subject": "Teste",
					"type": "",
					"communication_date": frappe.utils.now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_gerar_tarefa_sem_proximos_passos_nao_cria(self):
		com = create_test_case_communication(generate_task=1, next_steps=None)
		com.reload()
		self.assertFalse(com.legal_task)

	def test_gerar_tarefa_apos_primeiro_save(self):
		com = create_test_case_communication(next_steps="Ligar na segunda-feira")
		self.assertFalse(com.legal_task)
		com.generate_task = 1
		com.save(ignore_permissions=True)
		com.reload()
		self.assertTrue(com.legal_task)
		tarefa = frappe.get_doc("Legal Task", com.legal_task)
		self.assertEqual(
			frappe.utils.getdate(tarefa.due_date),
			frappe.utils.getdate(frappe.utils.add_days(frappe.utils.today(), 3)),
		)
