import os
import tempfile

import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


def _create_test_template():
	try:
		from docx import Document as DocxDocument
	except ImportError:
		return None

	with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
		doc = DocxDocument()
		doc.add_paragraph("Template kit teste {{ cliente_nome }}")
		doc.save(tmp.name)
		tmp_path = tmp.name

	try:
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"template_kit_{frappe.generate_hash(length=6)}.docx",
				"file_url": f"/private/files/template_kit_{frappe.generate_hash(length=6)}.docx",
				"is_private": 1,
			}
		)
		with open(tmp_path, "rb") as f:
			file_doc.content = f.read()
		file_doc.save(ignore_permissions=True)

		template = frappe.get_doc(
			{
				"doctype": "Template Documento",
				"titulo": _uid("Template Kit"),
				"tipo_documento": "Contrato",
				"arquivo": file_doc.file_url,
				"habilitado": 1,
			}
		).insert(ignore_permissions=True)
		return template.name
	finally:
		if os.path.exists(tmp_path):
			os.unlink(tmp_path)


class TestKitDeDocumentos(FrappeTestCase):
	def setUp(self):
		self.template_name = _create_test_template()
		if not self.template_name:
			self.skipTest("python-docx não instalado")

	def tearDown(self):
		frappe.db.rollback()

	def test_create_kit_com_template(self):
		titulo = _uid("Kit Teste")
		kit = frappe.get_doc(
			{
				"doctype": "Kit de Documentos",
				"titulo": titulo,
				"templates": [{"template": self.template_name, "ordem": 0}],
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Kit de Documentos", kit.name))
		self.assertEqual(kit.titulo, titulo)
		self.assertEqual(len(kit.templates), 1)
		self.assertEqual(kit.templates[0].template, self.template_name)

	def test_read_kit(self):
		titulo = _uid("Kit Read")
		kit = frappe.get_doc(
			{
				"doctype": "Kit de Documentos",
				"titulo": titulo,
				"templates": [{"template": self.template_name, "ordem": 1}],
			}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Kit de Documentos", kit.name)
		self.assertEqual(loaded.titulo, titulo)
		self.assertEqual(loaded.templates[0].ordem, 1)

	def test_update_kit_templates(self):
		titulo = _uid("Kit Update")
		kit = frappe.get_doc(
			{
				"doctype": "Kit de Documentos",
				"titulo": titulo,
				"templates": [{"template": self.template_name, "ordem": 0}],
			}
		).insert(ignore_permissions=True)
		kit.append("templates", {"template": self.template_name, "ordem": 1})
		kit.save(ignore_permissions=True)
		reloaded = frappe.get_doc("Kit de Documentos", kit.name)
		self.assertEqual(len(reloaded.templates), 2)
		reloaded.templates = reloaded.templates[:1]
		reloaded.save(ignore_permissions=True)
		self.assertEqual(len(frappe.get_doc("Kit de Documentos", kit.name).templates), 1)

	def test_titulo_obrigatorio_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Kit de Documentos",
					"templates": [{"template": self.template_name, "ordem": 0}],
				}
			).insert(ignore_permissions=True)

	def test_templates_obrigatorio_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Kit de Documentos",
					"titulo": _uid("Kit Sem Template"),
				}
			).insert(ignore_permissions=True)

	def test_titulo_duplicado_falha(self):
		titulo = _uid("Kit Dup")
		frappe.get_doc(
			{
				"doctype": "Kit de Documentos",
				"titulo": titulo,
				"templates": [{"template": self.template_name, "ordem": 0}],
			}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{
					"doctype": "Kit de Documentos",
					"titulo": titulo,
					"templates": [{"template": self.template_name, "ordem": 0}],
				}
			).insert(ignore_permissions=True)
