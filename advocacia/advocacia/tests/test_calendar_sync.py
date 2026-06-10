import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import create_test_hearing, create_test_prazo


class TestCalendarSync(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _find_event(self, source_doctype, source_name):
		return frappe.db.get_value(
			"Event",
			{"custom_source_doctype": source_doctype, "custom_source_name": source_name},
			["name", "subject", "status", "all_day", "color"],
			as_dict=True,
		)

	def test_hearing_cria_event(self):
		aud = create_test_hearing(type="Instrução")
		event = self._find_event("Hearing", aud.name)
		self.assertTrue(event)
		self.assertIn("Instrução", event.subject)

	def test_hearing_atualiza_event(self):
		aud = create_test_hearing(type="Conciliação")
		aud.type = "Julgamento"
		aud.save(ignore_permissions=True)
		event = self._find_event("Hearing", aud.name)
		self.assertIn("Julgamento", event.subject)

	def test_hearing_cancelada_fecha_event(self):
		aud = create_test_hearing()
		aud.status = "Cancelada"
		aud.save(ignore_permissions=True)
		event = self._find_event("Hearing", aud.name)
		self.assertEqual(event.status, "Closed")

	def test_prazo_cria_event_all_day(self):
		prazo = create_test_prazo(priority="Alta")
		event = self._find_event("Deadline", prazo.name)
		self.assertTrue(event)
		self.assertEqual(event.all_day, 1)
		self.assertEqual(event.color, "red")

	def test_prazo_concluido_fecha_event(self):
		prazo = create_test_prazo()
		prazo.status = "Concluído"
		prazo.save(ignore_permissions=True)
		event = self._find_event("Deadline", prazo.name)
		self.assertEqual(event.status, "Closed")

	def test_prazo_prioridade_media_cor_laranja(self):
		prazo = create_test_prazo(priority="Média")
		event = self._find_event("Deadline", prazo.name)
		self.assertEqual(event.color, "orange")
