import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.painel import get as get_painel_payload
from advocacia.advocacia.painel.operational import get_active_cases_enriched
from advocacia.advocacia.tests.test_setup import create_test_legal_case, create_test_prazo


class TestPainelModulos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_payload_includes_modular_keys(self):
		data = get_painel_payload()
		for key in ("saude_operacional", "atencao", "proximo_evento", "active_cases"):
			self.assertIn(key, data)
		self.assertNotIn("agenda_dias", data)

	def test_saude_operacional_structure(self):
		if "Advocacia Manager" not in frappe.get_roles():
			return
		data = get_painel_payload()
		saude = data["saude_operacional"]
		self.assertIn("score", saude)
		self.assertIn("tone", saude)
		self.assertIn("label", saude)
		self.assertIn("breakdown", saude)

	def test_atencao_structure(self):
		data = get_painel_payload()
		atencao = data["atencao"]
		self.assertIn("tiles", atencao)
		self.assertIn("all_clear", atencao)

	def test_proximo_evento_is_list(self):
		data = get_painel_payload()
		self.assertIsInstance(data["proximo_evento"], list)

	def test_active_cases_enriched_next_deadline(self):
		case = create_test_legal_case(status="Em andamento")
		create_test_prazo(servico=case.name, description="Prazo teste hub")
		rows = get_active_cases_enriched(10)
		match = [row for row in rows if row["name"] == case.name]
		self.assertTrue(match)
		self.assertTrue(match[0].get("next_event_label"))
