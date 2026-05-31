import io
import os
import tempfile

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.documentos import (
	get_placeholders_disponiveis,
	get_templates_disponiveis,
)
from advocacia.advocacia.tests.test_setup import create_test_servico


class TestDocumentos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_templates_vazio_ou_lista(self):
		result = get_templates_disponiveis()
		self.assertIsInstance(result, list)

	def test_get_placeholders_tem_grupos(self):
		result = get_placeholders_disponiveis()
		self.assertIsInstance(result, dict)
		self.assertIn("Servico", result)
		self.assertIn("Cliente", result)

	def test_get_placeholders_legacy(self):
		result = get_placeholders_disponiveis()
		aliases = result.get("Aliases Legados", [])
		names = [p.get("placeholder") for p in aliases]
		self.assertIn("nome", names)
		self.assertIn("cpf", names)

	def test_gerar_documento_template_inexistente(self):
		from advocacia.advocacia.documentos import gerar_documento

		servico = create_test_servico()
		with self.assertRaises(Exception):
			gerar_documento(servico.name, "Template Inexistente XYZ")

	def test_gerar_documento_com_template_minimo(self):
		try:
			from docxtpl import DocxTemplate
		except ImportError:
			self.skipTest("docxtpl não instalado")

		from docx import Document as DocxDocument

		from advocacia.advocacia.documentos import gerar_documento

		servico = create_test_servico()

		with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
			doc = DocxDocument()
			doc.add_paragraph("Cliente: {{ nome }}")
			doc.add_paragraph("Serviço: {{ servico }}")
			doc.save(tmp.name)
			tmp_path = tmp.name

		try:
			file_doc = frappe.get_doc(
				{
					"doctype": "File",
					"file_name": "template_teste.docx",
					"file_url": "/private/files/template_teste.docx",
					"is_private": 1,
				}
			)
			# Usar File attach via content
			with open(tmp_path, "rb") as f:
				content = f.read()
			file_doc.content = content
			file_doc.save(ignore_permissions=True)

			template = frappe.get_doc(
				{
					"doctype": "Template Documento",
					"titulo": f"Template Teste {frappe.generate_hash(length=4)}",
					"tipo_documento": "Contrato",
					"arquivo": file_doc.file_url,
					"habilitado": 1,
				}
			)
			template.insert(ignore_permissions=True)

			result = gerar_documento(servico.name, template.name)
			self.assertIn("file_url", result)
			self.assertTrue(result["file_url"])
		finally:
			if os.path.exists(tmp_path):
				os.unlink(tmp_path)
