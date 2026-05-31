import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import create_test_audiencia, create_test_prazo


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

	def test_audiencia_cria_event(self):
		aud = create_test_audiencia(tipo="Instrução")
		event = self._find_event("Audiencia", aud.name)
		self.assertTrue(event)
		self.assertIn("Instrução", event.subject)

	def test_audiencia_atualiza_event(self):
		aud = create_test_audiencia(tipo="Conciliação")
		aud.tipo = "Julgamento"
		aud.save(ignore_permissions=True)
		event = self._find_event("Audiencia", aud.name)
		self.assertIn("Julgamento", event.subject)

	def test_audiencia_cancelada_fecha_event(self):
		aud = create_test_audiencia()
		aud.status_aud = "Cancelada"
		aud.save(ignore_permissions=True)
		event = self._find_event("Audiencia", aud.name)
		self.assertEqual(event.status, "Closed")

	def test_prazo_cria_event_all_day(self):
		prazo = create_test_prazo(prioridade="Alta")
		event = self._find_event("Controle de Prazos", prazo.name)
		self.assertTrue(event)
		self.assertEqual(event.all_day, 1)
		self.assertEqual(event.color, "red")

	def test_prazo_concluido_fecha_event(self):
		prazo = create_test_prazo()
		prazo.status = "Concluído"
		prazo.save(ignore_permissions=True)
		event = self._find_event("Controle de Prazos", prazo.name)
		self.assertEqual(event.status, "Closed")

	def test_prazo_prioridade_media_cor_laranja(self):
		prazo = create_test_prazo(prioridade="Média")
		event = self._find_event("Controle de Prazos", prazo.name)
		self.assertEqual(event.color, "orange")
