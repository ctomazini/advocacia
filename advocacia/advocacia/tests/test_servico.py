import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	VALID_CNJ,
	VALID_CNJ_DIGITS,
	create_test_acordo,
	create_test_audiencia,
	create_test_cliente,
	create_test_servico,
)


class TestServico(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_consultoria_salva(self):
		servico = create_test_servico(tipo="Consultoria")
		self.assertEqual(servico.tipo, "Consultoria")
		self.assertEqual(servico.status, "Em andamento")

	def test_processo_judicial_cnj_valido(self):
		servico = create_test_servico(
			tipo="Processo Judicial",
			numero_processo=VALID_CNJ,
		)
		self.assertEqual(servico.numero_processo, VALID_CNJ_DIGITS)

	def test_processo_judicial_sem_cnj_salva(self):
		servico = create_test_servico(
			tipo="Processo Judicial",
			numero_processo="",
		)
		self.assertIsNone(servico.numero_processo)

	def test_processo_legado_aceita_texto_livre(self):
		servico = create_test_servico(
			tipo="Processo Judicial",
			numeracao_legada=1,
			numero_processo="12345/2000",
		)
		self.assertEqual(servico.numero_processo, "12345/2000")

	def test_sem_cliente_falha(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc({"doctype": "Servico", "tipo": "Consultoria"}).insert(
				ignore_permissions=True
			)

	def test_cnj_invalido_falha(self):
		cliente = create_test_cliente().name
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Servico",
					"cliente": cliente,
					"tipo": "Processo Judicial",
					"numero_processo": "1234",
				}
			).insert(ignore_permissions=True)

	def test_alterar_status_encerrado(self):
		servico = create_test_servico()
		servico.status = "Encerrado"
		servico.save(ignore_permissions=True)
		self.assertEqual(servico.status, "Encerrado")

	def test_acordo_vinculado_ao_servico(self):
		servico = create_test_servico()
		acordo = create_test_acordo(servico=servico.name, num_parcelas=1, valor_total=5000)
		vinculados = frappe.get_all(
			"Acordo de Honorarios Processuais",
			filters={"servico": servico.name},
			pluck="name",
		)
		self.assertIn(acordo.name, vinculados)

	def test_audiencia_vinculada_ao_servico(self):
		servico = create_test_servico()
		aud = create_test_audiencia(servico=servico.name)
		vinculadas = frappe.get_all(
			"Audiencia", filters={"servico": servico.name}, pluck="name"
		)
		self.assertIn(aud.name, vinculadas)

	def test_titulo_composto(self):
		cliente = create_test_cliente()
		servico = create_test_servico(cliente=cliente.name)
		self.assertIn(servico.name, servico.title)
		self.assertIn(cliente.nome, servico.title)
