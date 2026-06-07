import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.painel import get as get_painel_payload


class TestPainelModulos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_payload_includes_modular_keys(self):
		data = get_painel_payload()
		for key in ("saude_operacional", "atencao", "agenda_dias", "proximo_evento"):
			self.assertIn(key, data)

	def test_saude_operacional_structure(self):
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

	def test_agenda_dias_is_list(self):
		data = get_painel_payload(periodo_dias=7)
		self.assertIsInstance(data["agenda_dias"], list)
		self.assertLessEqual(len(data["agenda_dias"]), 7)

	def test_proximo_evento_is_list(self):
		data = get_painel_payload()
		self.assertIsInstance(data["proximo_evento"], list)
