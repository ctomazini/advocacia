import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	VALID_CNJ,
	VALID_CNJ_DIGITS,
	create_test_acordo,
	create_test_hearing,
	create_test_client,
	create_test_legal_case,
)


class TestLegalCase(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_consultoria_salva(self):
		servico = create_test_legal_case(tipo="Consultoria")
		self.assertEqual(servico.tipo, "Consultoria")
		self.assertEqual(servico.status, "Em andamento")

	def test_processo_judicial_cnj_valido(self):
		servico = create_test_legal_case(
			tipo="Processo Judicial",
			numero_processo=VALID_CNJ,
		)
		self.assertEqual(servico.numero_processo, VALID_CNJ_DIGITS)

	def test_processo_judicial_sem_cnj_salva(self):
		servico = create_test_legal_case(
			tipo="Processo Judicial",
			numero_processo="",
		)
		self.assertIsNone(servico.numero_processo)

	def test_processo_legado_aceita_texto_livre(self):
		servico = create_test_legal_case(
			tipo="Processo Judicial",
			numeracao_legada=1,
			numero_processo="12345/2000",
		)
		self.assertEqual(servico.numero_processo, "12345/2000")

	def test_sem_cliente_falha(self):
		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc({"doctype": "Legal Case", "tipo": "Consultoria"}).insert(
				ignore_permissions=True
			)

	def test_cnj_invalido_falha(self):
		cliente = create_test_client().name
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Legal Case",
					"client": cliente,
					"tipo": "Processo Judicial",
					"numero_processo": "1234",
				}
			).insert(ignore_permissions=True)

	def test_alterar_status_encerrado(self):
		servico = create_test_legal_case()
		servico.status = "Encerrado"
		servico.save(ignore_permissions=True)
		self.assertEqual(servico.status, "Encerrado")

	def test_acordo_vinculado_ao_servico(self):
		servico = create_test_legal_case()
		acordo = create_test_acordo(servico=servico.name, num_parcelas=1, valor_total=5000)
		vinculados = frappe.get_all(
			"Fee Agreement",
			filters={"legal_case": servico.name},
			pluck="name",
		)
		self.assertIn(acordo.name, vinculados)

	def test_hearing_vinculada_ao_servico(self):
		servico = create_test_legal_case()
		aud = create_test_hearing(servico=servico.name)
		vinculadas = frappe.get_all(
			"Hearing", filters={"legal_case": servico.name}, pluck="name"
		)
		self.assertIn(aud.name, vinculadas)

	def test_titulo_composto(self):
		cliente = create_test_client()
		servico = create_test_legal_case(cliente=cliente.name)
		self.assertIn(servico.name, servico.title)
		self.assertIn(cliente.nome, servico.title)

	def test_dashboard_links_filtram_por_servico(self):
		meta = frappe.get_meta("Legal Case")
		dashboard = meta.get_dashboard_data()
		linked = {
			row.link_doctype: row.link_fieldname
			for row in (meta.links or [])
			if row.link_doctype and row.link_fieldname and not row.is_child_table
		}
		expected = {
			"Fee Agreement": "legal_case",
			"Service Record": "legal_case",
			"Hearing": "legal_case",
			"Deadline": "legal_case",
			"Court Cost": "legal_case",
			"Case Communication": "legal_case",
			"Time Entry": "legal_case",
			"Legal Task": "legal_case",
			"Legal Payment": "legal_case",
		}
		self.assertEqual(linked, expected)
		self.assertEqual(dashboard.fieldname, "legal_case")
		for doctype, fieldname in expected.items():
			self.assertEqual(dashboard.non_standard_fieldnames.get(doctype), fieldname)

	def test_get_open_count_registro_de_atos_por_servico(self):
		from frappe.desk.notifications import get_open_count

		servico = create_test_legal_case()
		registro = frappe.get_doc(
			{
				"doctype": "Service Record",
				"legal_case": servico.name,
				"client": servico.client,
				"status": "Aberto",
			}
		).insert(ignore_permissions=True)

		result = get_open_count("Legal Case", servico.name)
		atos = next(
			row
			for row in result["count"]["external_links_found"]
			if row["doctype"] == "Service Record"
		)
		self.assertGreaterEqual(atos["count"], 1)
		names = frappe.get_all(
			"Service Record", filters={"legal_case": servico.name}, pluck="name"
		)
		self.assertIn(registro.name, names)
