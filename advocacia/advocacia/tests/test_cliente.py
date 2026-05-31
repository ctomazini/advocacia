import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	VALID_CELULAR,
	VALID_CNPJ,
	VALID_CPF,
	VALID_CPF_DIGITS,
	VALID_EMAIL,
	VALID_FIXO,
	_gerar_cpf_valido,
	create_test_cliente,
)


class TestCliente(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_criar_pf_valido(self):
		cpf = _gerar_cpf_valido()
		cliente = create_test_cliente(
			tipo_pessoa="Pessoa Física",
			nome=f"Maria Teste {frappe.generate_hash(length=6)}",
			cpf=cpf,
		)
		self.assertEqual(cliente.tipo_pessoa, "Pessoa Física")
		self.assertEqual(cliente.cpf, cpf)
		self.assertTrue(frappe.db.exists("Cliente", cliente.name))

	def test_criar_pj_valido(self):
		cliente = create_test_cliente(
			tipo_pessoa="Pessoa Jurídica",
			nome=f"Empresa Teste {frappe.generate_hash(length=6)}",
			cnpj=VALID_CNPJ,
		)
		self.assertEqual(cliente.tipo_pessoa, "Pessoa Jurídica")
		self.assertTrue(frappe.db.exists("Cliente", cliente.name))

	def test_pf_com_contatos(self):
		cliente = create_test_cliente(
			contatos=[
				{
					"nome": "Contato Teste",
					"telefone": VALID_FIXO,
					"celular": VALID_CELULAR,
					"email": VALID_EMAIL,
				}
			]
		)
		self.assertEqual(len(cliente.contatos), 1)
		self.assertIn("@", cliente.contatos[0].email)

	def test_pf_com_endereco(self):
		cliente = create_test_cliente(
			enderecos=[
				{
					"logradouro": "Rua Teste 123",
					"cep": "01310-100",
					"cidade": "São Paulo",
					"estado": "SP",
				}
			]
		)
		self.assertEqual(cliente.enderecos[0].logradouro, "Rua Teste 123")

	def test_pj_com_representante(self):
		cliente = create_test_cliente(
			tipo_pessoa="Pessoa Jurídica",
			representante="João Representante",
			cpf_representante=_gerar_cpf_valido(),
		)
		self.assertEqual(cliente.representante, "João Representante")

	def test_pf_sem_nome_falha(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Física",
					"cpf": VALID_CPF,
				}
			).insert(ignore_permissions=True)

	def test_cpf_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_cliente(cpf="123")

	def test_cpf_sequencia_repetida_falha(self):
		with self.assertRaises(ValidationError):
			create_test_cliente(cpf="111.111.111-11")

	def test_cnpj_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_cliente(
				tipo_pessoa="Pessoa Jurídica",
				cnpj="123",
			)

	def test_email_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_cliente(
				contatos=[{"nome": "X", "email": "invalido@"}],
			)

	def test_telefone_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_cliente(
				contatos=[{"nome": "X", "telefone": "123"}],
			)

	def test_cpf_duplicado_falha(self):
		cpf_fixo = _gerar_cpf_valido()
		create_test_cliente(nome=f"Cliente Dup A {frappe.generate_hash(length=6)}", cpf=cpf_fixo)
		with self.assertRaises(ValidationError):
			create_test_cliente(
				nome=f"Cliente Dup B {frappe.generate_hash(length=6)}",
				cpf=cpf_fixo,
			)