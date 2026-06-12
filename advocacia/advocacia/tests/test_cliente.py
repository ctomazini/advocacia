import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	VALID_CELULAR,
	VALID_CPF,
	VALID_CPF_DIGITS,
	VALID_EMAIL,
	VALID_FIXO,
	_gerar_cnpj_valido,
	_gerar_cpf_valido,
	create_test_client,
)


class TestClient(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_criar_pf_valido(self):
		cpf = _gerar_cpf_valido()
		cliente = create_test_client(
			person_type="Pessoa Física",
			client_name=f"Maria Teste {frappe.generate_hash(length=6)}",
			cpf=cpf,
		)
		self.assertEqual(cliente.person_type, "Pessoa Física")
		self.assertEqual(cliente.cpf, cpf)
		self.assertTrue(frappe.db.exists("Client", cliente.name))

	def test_criar_pj_valido(self):
		cliente = create_test_client(
			person_type="Pessoa Jurídica",
			client_name=f"Empresa Teste {frappe.generate_hash(length=6)}",
			cnpj=_gerar_cnpj_valido(),
		)
		self.assertEqual(cliente.person_type, "Pessoa Jurídica")
		self.assertTrue(frappe.db.exists("Client", cliente.name))

	def test_pf_com_contatos(self):
		cliente = create_test_client(
			contacts=[
				{
					"contact_name": "Contato Teste",
					"phone": VALID_FIXO,
					"mobile": VALID_CELULAR,
					"email": VALID_EMAIL,
				}
			]
		)
		self.assertEqual(len(cliente.contacts), 1)
		self.assertIn("@", cliente.contacts[0].email)

	def test_pf_com_endereco(self):
		cliente = create_test_client(
			addresses=[
				{
					"street": "Rua Teste 123",
					"cep": "01310-100",
					"city": "São Paulo",
					"state": "SP",
				}
			]
		)
		self.assertEqual(cliente.addresses[0].street, "Rua Teste 123")

	def test_pj_com_representante(self):
		cliente = create_test_client(
			person_type="Pessoa Jurídica",
			representative="João Representante",
			representative_cpf=_gerar_cpf_valido(),
		)
		self.assertEqual(cliente.representative, "João Representante")

	def test_pf_sem_nome_falha(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Client",
					"person_type": "Pessoa Física",
					"cpf": VALID_CPF,
				}
			).insert(ignore_permissions=True)

	def test_cpf_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_client(cpf="123")

	def test_cpf_sequencia_repetida_falha(self):
		with self.assertRaises(ValidationError):
			create_test_client(cpf="111.111.111-11")

	def test_cnpj_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_client(
				person_type="Pessoa Jurídica",
				cnpj="123",
			)

	def test_email_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_client(
				contacts=[{"contact_name": "X", "email": "invalido@"}],
			)

	def test_telefone_invalido_falha(self):
		with self.assertRaises(ValidationError):
			create_test_client(
				contacts=[{"contact_name": "X", "phone": "123"}],
			)

	def test_cpf_duplicado_falha(self):
		cpf_fixo = _gerar_cpf_valido()
		create_test_client(client_name=f"Client Dup A {frappe.generate_hash(length=6)}", cpf=cpf_fixo)
		with self.assertRaises(ValidationError):
			create_test_client(
				client_name=f"Client Dup B {frappe.generate_hash(length=6)}",
				cpf=cpf_fixo,
			)

	def test_nome_duplicado_com_cpf_diferente_ok(self):
		nome = f"Maria Silva {frappe.generate_hash(length=6)}"
		cliente_a = create_test_client(client_name=nome, cpf=_gerar_cpf_valido())
		cliente_b = create_test_client(client_name=nome, cpf=_gerar_cpf_valido())
		self.assertEqual(cliente_a.client_name, cliente_b.client_name)
		self.assertNotEqual(cliente_a.name, cliente_b.name)
		self.assertNotEqual(cliente_a.cpf, cliente_b.cpf)

	def test_birth_date_and_rg_issuer(self):
		cliente_pf = create_test_client(
			cpf=_gerar_cpf_valido(),
			birth_date="1990-06-15",
			rg_issuer="SSP/RS",
		)
		self.assertEqual(str(cliente_pf.birth_date), "1990-06-15")
		self.assertEqual(cliente_pf.rg_issuer, "SSP/RS")

		cliente_pj = create_test_client(
			person_type="Pessoa Jurídica",
			cnpj=_gerar_cnpj_valido(),
			birth_date="1990-06-15",
			rg_issuer="SSP/RS",
		)
		self.assertIsNone(cliente_pj.birth_date)
		self.assertIsNone(cliente_pj.rg_issuer)