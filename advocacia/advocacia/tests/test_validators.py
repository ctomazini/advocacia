import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.validators import (
	validar_cnpj,
	validar_cnj,
	validar_cpf,
	validar_email,
	validar_telefone,
)
from advocacia.advocacia.tests.test_setup import (
	VALID_CELULAR,
	VALID_CNPJ,
	VALID_CNPJ_DIGITS,
	VALID_CNJ,
	VALID_CNJ_DIGITS,
	VALID_CPF,
	VALID_CPF_DIGITS,
	VALID_EMAIL,
	VALID_FIXO,
)


class TestValidators(FrappeTestCase):
	def test_cpf_formatado_valido(self):
		self.assertEqual(validar_cpf(VALID_CPF), VALID_CPF_DIGITS)

	def test_cpf_digitos_valido(self):
		self.assertEqual(validar_cpf(VALID_CPF_DIGITS), VALID_CPF_DIGITS)

	def test_cpf_sequencia_invalida(self):
		with self.assertRaises(ValidationError):
			validar_cpf("111.111.111-11")

	def test_cpf_curto_invalido(self):
		with self.assertRaises(ValidationError):
			validar_cpf("123")

	def test_cpf_vazio(self):
		self.assertEqual(validar_cpf(""), "")

	def test_cnpj_formatado_valido(self):
		self.assertEqual(validar_cnpj(VALID_CNPJ), VALID_CNPJ_DIGITS)

	def test_cnpj_sequencia_invalida(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("00.000.000/0000-00")

	def test_cnpj_curto_invalido(self):
		with self.assertRaises(ValidationError):
			validar_cnpj("123")

	def test_celular_valido(self):
		self.assertEqual(validar_telefone(VALID_CELULAR, phone_type="mobile"), VALID_CELULAR)

	def test_fixo_valido(self):
		self.assertEqual(validar_telefone(VALID_FIXO, phone_type="landline"), VALID_FIXO)

	def test_telefone_curto_invalido(self):
		with self.assertRaises(ValidationError):
			validar_telefone("123", phone_type="mobile")

	def test_cnj_formatado_valido(self):
		self.assertEqual(validar_cnj(VALID_CNJ), VALID_CNJ_DIGITS)

	def test_cnj_curto_invalido(self):
		with self.assertRaises(ValidationError):
			validar_cnj("123")

	def test_email_valido(self):
		self.assertEqual(validar_email(VALID_EMAIL), VALID_EMAIL.lower())

	def test_email_invalido(self):
		with self.assertRaises(ValidationError):
			validar_email("user@")

	def test_email_sem_dominio(self):
		with self.assertRaises(ValidationError):
			validar_email("user")
