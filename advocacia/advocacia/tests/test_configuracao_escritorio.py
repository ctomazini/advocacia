import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase


class TestConfiguracaoEscritorio(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_read_single(self):
		cfg = frappe.get_single("Office Settings")
		self.assertEqual(cfg.doctype, "Office Settings")

	def test_update_single(self):
		cfg = frappe.get_single("Office Settings")
		cfg.razao_social = "Escritório Teste Advocacia LTDA"
		cfg.advogada = "Dra. Teste"
		cfg.oab = "OAB/RS 123456"
		cfg.endereco = "Rua Teste, 100, Porto Alegre/RS"
		cfg.cnpj = "11222333000181"
		cfg.bank_name = "Banco Teste"
		cfg.bank_agency = "1234"
		cfg.bank_account = "56789-0"
		cfg.bank_pix = "teste@exemplo.com"
		cfg.default_notify_days = 5
		cfg.save(ignore_permissions=True)

		reloaded = frappe.get_single("Office Settings")
		self.assertEqual(reloaded.razao_social, "Escritório Teste Advocacia LTDA")
		self.assertEqual(reloaded.advogada, "Dra. Teste")
		self.assertEqual(reloaded.oab, "OAB/RS 123456")
		self.assertEqual(reloaded.bank_name, "Banco Teste")
		self.assertEqual(reloaded.default_notify_days, 5)

	def test_required_razao_social_falha(self):
		cfg = frappe.get_single("Office Settings")
		original = cfg.razao_social
		cfg.razao_social = ""
		with self.assertRaises(ValidationError):
			cfg.save(ignore_permissions=True)
		cfg.razao_social = original

	def test_required_advogada_falha(self):
		cfg = frappe.get_single("Office Settings")
		original = cfg.advogada
		cfg.advogada = ""
		with self.assertRaises(ValidationError):
			cfg.save(ignore_permissions=True)
		cfg.advogada = original

	def test_required_oab_falha(self):
		cfg = frappe.get_single("Office Settings")
		original = cfg.oab
		cfg.oab = ""
		with self.assertRaises(ValidationError):
			cfg.save(ignore_permissions=True)
		cfg.oab = original

	def test_required_endereco_falha(self):
		cfg = frappe.get_single("Office Settings")
		original = cfg.endereco
		cfg.endereco = ""
		with self.assertRaises(ValidationError):
			cfg.save(ignore_permissions=True)
		cfg.endereco = original
