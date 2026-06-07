import frappe
from frappe.exceptions import MandatoryError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.tests.test_setup import create_test_legal_case, create_test_legal_task


class TestLegalTask(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_legal_task_avulsa(self):
		tarefa = create_test_legal_task()
		self.assertEqual(tarefa.status, "Pendente")
		self.assertFalse(tarefa.legal_case)

	def test_legal_task_com_servico(self):
		servico = create_test_legal_case()
		tarefa = create_test_legal_task(servico=servico.name)
		self.assertEqual(tarefa.legal_case, servico.name)
		self.assertEqual(tarefa.client, servico.client)

	def test_client_via_servico(self):
		servico = create_test_legal_case()
		tarefa = frappe.get_doc(
			{
				"doctype": "Legal Task",
				"titulo": "Legal Task com serviço",
				"legal_case": servico.name,
				"status": "Pendente",
			}
		)
		tarefa.insert(ignore_permissions=True)
		self.assertEqual(tarefa.client, servico.client)

	def test_concluir(self):
		tarefa = create_test_legal_task()
		result = tarefa.concluir()
		tarefa.reload()
		self.assertEqual(result["status"], "Concluída")
		self.assertEqual(tarefa.status, "Concluída")
		self.assertEqual(str(tarefa.data_conclusao), str(today()))

	def test_sem_titulo_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc({"doctype": "Legal Task", "status": "Pendente"}).insert(
				ignore_permissions=True
			)
