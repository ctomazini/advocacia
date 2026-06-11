import os

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import (
	create_test_legal_case,
	create_test_prazo,
	ensure_test_document_category,
)


def _create_test_file_url():
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"case_doc_{frappe.generate_hash(length=6)}.txt",
			"content": b"test case document",
			"is_private": 1,
		}
	)
	file_doc.save(ignore_permissions=True)
	return file_doc.file_url


class TestCaseDocument(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_case_document(self):
		case = create_test_legal_case()
		ensure_test_document_category("Petição")
		doc = frappe.get_doc(
			{
				"doctype": "Case Document",
				"legal_case": case.name,
				"category": "Petição",
				"status": "Rascunho",
				"source": "Upload Manual",
				"file": _create_test_file_url(),
			}
		).insert(ignore_permissions=True)

		self.assertTrue(doc.name.startswith("DOC-"))
		self.assertEqual(doc.category, "Petição")
		self.assertEqual(doc.client, case.client)
		self.assertIn("Petição", doc.title)
		self.assertIn(case.name, doc.title)

	def test_auto_compose_title(self):
		case = create_test_legal_case()
		ensure_test_document_category("Procuração")
		doc = frappe.get_doc(
			{
				"doctype": "Case Document",
				"legal_case": case.name,
				"category": "Procuração",
				"status": "Rascunho",
				"file": _create_test_file_url(),
				"version_label": "Rev_01",
			}
		).insert(ignore_permissions=True)

		self.assertIn("Procuração", doc.title)
		self.assertIn("Rev_01", doc.title)

	def test_deadline_validation(self):
		case_a = create_test_legal_case()
		case_b = create_test_legal_case()
		deadline = create_test_prazo(servico=case_b.name)
		ensure_test_document_category("Protocolo")

		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Case Document",
					"legal_case": case_a.name,
					"category": "Protocolo",
					"status": "Protocolado",
					"file": _create_test_file_url(),
					"related_deadline": deadline.name,
				}
			).insert(ignore_permissions=True)

	def test_status_options(self):
		meta = frappe.get_meta("Case Document")
		status_field = meta.get_field("status")
		options = [option.strip() for option in (status_field.options or "").split("\n")]
		for expected in ("Rascunho", "Assinado", "Protocolado", "Juntado", "Substituído"):
			self.assertIn(expected, options)
