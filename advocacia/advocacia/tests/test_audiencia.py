import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today

from advocacia.advocacia.doctype.hearing.hearing import get_events
from advocacia.advocacia.tests.test_setup import create_test_hearing, create_test_legal_case


class TestHearing(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_hearing_presencial_salva(self):
		aud = create_test_hearing()
		self.assertEqual(aud.modalidade, "Presencial")
		self.assertEqual(aud.status_aud or "Agendada", "Agendada")

	def test_client_via_servico(self):
		servico = create_test_legal_case()
		aud = create_test_hearing(servico=servico.name)
		self.assertEqual(aud.client, servico.client)

	def test_get_events_no_periodo(self):
		aud = create_test_hearing(data_hora=now_datetime())
		start = add_days(today(), -1)
		end = add_days(today(), 1)
		events = get_events(start, end)
		names = [e["name"] for e in events]
		self.assertIn(aud.name, names)

	def test_sem_servico_falha(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Hearing",
					"data_hora": now_datetime(),
					"tipo": "Conciliação",
				}
			).insert(ignore_permissions=True)

	def test_status_realizada(self):
		aud = create_test_hearing()
		aud.status_aud = "Realizada"
		aud.save(ignore_permissions=True)
		self.assertEqual(aud.status_aud, "Realizada")

	def test_hearing_virtual(self):
		aud = create_test_hearing(modalidade="Virtual", link_virtual="https://meet.example.com/x")
		self.assertEqual(aud.modalidade, "Virtual")

	def test_titulo_composto(self):
		servico = create_test_legal_case()
		cliente_nome = frappe.db.get_value("Client", servico.client, "nome")
		aud = create_test_hearing(servico=servico.name, tipo="Instrução")
		self.assertIn(aud.name, aud.title)
		self.assertIn(cliente_nome, aud.title)
