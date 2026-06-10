import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.doctype.deadline.deadline import get_events
from advocacia.advocacia.tests.test_setup import create_test_prazo, create_test_legal_case


class TestControlePrazos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_prazo_futuro_pendente(self):
		prazo = create_test_prazo(due_date=add_days(today(), 10))
		self.assertEqual(prazo.status or "Pendente", "Pendente")

	def test_prioridade_alta(self):
		prazo = create_test_prazo(priority="Alta")
		self.assertEqual(prazo.priority, "Alta")

	def test_client_via_servico(self):
		servico = create_test_legal_case()
		prazo = create_test_prazo(servico=servico.name)
		self.assertEqual(prazo.client, servico.client)

	def test_titulo_composto(self):
		servico = create_test_legal_case()
		cliente_nome = frappe.db.get_value("Client", servico.client, "client_name")
		prazo = create_test_prazo(servico=servico.name, description="Contestação")
		self.assertIn(prazo.name, prazo.title)
		self.assertIn(cliente_nome, prazo.title)

	def test_get_events(self):
		prazo = create_test_prazo(due_date=today())
		events = get_events(add_days(today(), -1), add_days(today(), 1))
		names = [e["name"] for e in events]
		self.assertIn(prazo.name, names)

	def test_sem_servico_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Deadline",
					"due_date": today(),
					"description": "Sem serviço",
				}
			).insert(ignore_permissions=True)

	def test_sem_descricao_falha(self):
		servico = create_test_legal_case().name
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Deadline",
					"legal_case": servico,
					"due_date": today(),
				}
			).insert(ignore_permissions=True)
