import frappe
from frappe.exceptions import MandatoryError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	create_test_cliente,
	create_test_comunicacao,
	create_test_servico,
)


class TestComunicacao(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud_valido(self):
		com = create_test_comunicacao()
		self.assertTrue(com.name)

	def test_cliente_via_servico(self):
		servico = create_test_servico()
		cliente = frappe.db.get_value("Servico", servico.name, "cliente")
		com = frappe.get_doc(
			{
				"doctype": "Comunicacao",
				"servico": servico.name,
				"assunto": "Teste via serviço",
				"tipo": "Telefone",
				"data": frappe.utils.now_datetime(),
			}
		)
		com.insert(ignore_permissions=True)
		self.assertEqual(com.cliente, cliente)

	def test_gerar_tarefa_automatica(self):
		com = create_test_comunicacao(
			gerar_tarefa=1,
			proximos_passos="Retornar ligação amanhã",
		)
		com.reload()
		self.assertTrue(com.tarefa)
		tarefa = frappe.get_doc("Tarefa", com.tarefa)
		self.assertIn("Follow-up:", tarefa.titulo)

	def test_sem_assunto_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Comunicacao",
					"cliente": create_test_cliente().name,
					"tipo": "Telefone",
					"data": frappe.utils.now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_sem_tipo_falha(self):
		from frappe.exceptions import ValidationError

		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Comunicacao",
					"cliente": create_test_cliente().name,
					"assunto": "Teste",
					"tipo": "",
					"data": frappe.utils.now_datetime(),
				}
			).insert(ignore_permissions=True)

	def test_gerar_tarefa_sem_proximos_passos_nao_cria(self):
		com = create_test_comunicacao(gerar_tarefa=1, proximos_passos=None)
		com.reload()
		self.assertFalse(com.tarefa)

	def test_gerar_tarefa_apos_primeiro_save(self):
		com = create_test_comunicacao(proximos_passos="Ligar na segunda-feira")
		self.assertFalse(com.tarefa)
		com.gerar_tarefa = 1
		com.save(ignore_permissions=True)
		com.reload()
		self.assertTrue(com.tarefa)
		tarefa = frappe.get_doc("Tarefa", com.tarefa)
		self.assertEqual(
			frappe.utils.getdate(tarefa.data_limite),
			frappe.utils.getdate(frappe.utils.add_days(frappe.utils.today(), 3)),
		)
