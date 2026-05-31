import frappe
from frappe.exceptions import MandatoryError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.tests.test_setup import create_test_servico, create_test_tarefa


class TestTarefa(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_tarefa_avulsa(self):
		tarefa = create_test_tarefa()
		self.assertEqual(tarefa.status, "Pendente")
		self.assertFalse(tarefa.servico)

	def test_tarefa_com_servico(self):
		servico = create_test_servico()
		tarefa = create_test_tarefa(servico=servico.name)
		self.assertEqual(tarefa.servico, servico.name)

	def test_concluir(self):
		tarefa = create_test_tarefa()
		result = tarefa.concluir()
		tarefa.reload()
		self.assertEqual(result["status"], "Concluída")
		self.assertEqual(tarefa.status, "Concluída")
		self.assertEqual(str(tarefa.data_conclusao), str(today()))

	def test_sem_titulo_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc({"doctype": "Tarefa", "status": "Pendente"}).insert(
				ignore_permissions=True
			)
