import json
import os
import tempfile

import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.documentos import (
	_build_context,
	_formatar_data_extenso,
	gerar_documentos_em_lote,
	get_kits_disponiveis,
	get_placeholders_referencia,
	get_templates_disponiveis,
)
from advocacia.advocacia.tests.test_setup import create_test_servico


def _ensure_test_escritorio_config(advogada="Advogada Teste"):
	cfg = frappe.get_single("Configuracao do Escritorio")
	cfg.razao_social = "Escritorio Teste Advocacia"
	cfg.cnpj = "11222333000181"
	cfg.oab = "OAB/RS 00.000"
	cfg.advogada = advogada
	cfg.endereco = "Rua Teste, 100, Cidade Teste/RS"
	cfg.registro_sia = "00000"
	cfg.save(ignore_permissions=True)
	return cfg


class TestDocumentos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_templates_vazio_ou_lista(self):
		result = get_templates_disponiveis()
		self.assertIsInstance(result, list)

	def test_get_kits_lista(self):
		result = get_kits_disponiveis()
		self.assertIsInstance(result, list)

	def test_get_placeholders_referencia_grupos(self):
		result = get_placeholders_referencia()
		self.assertIsInstance(result, list)
		grupos = [bloco["grupo"] for bloco in result]
		self.assertIn("Escritório", grupos)
		self.assertIn("Cliente", grupos)
		self.assertIn("Serviço", grupos)

	def test_data_extenso_marco_com_cedilha(self):
		self.assertIn("março", _formatar_data_extenso("2026-03-15"))

	def test_build_context_escritorio_e_cliente(self):
		_ensure_test_escritorio_config()
		servico = create_test_servico()
		context = _build_context(servico.name)
		self.assertEqual(context["escritorio_advogada"], "Advogada Teste")
		self.assertEqual(context["escritorio_razao_social"], "Escritorio Teste Advocacia")
		self.assertTrue(context["cliente_nome"])
		self.assertEqual(context["nome"], context["cliente_nome"])
		self.assertIn("data_hoje", context)
		self.assertIn("data_hoje_extenso", context)

	def test_gerar_documentos_em_lote(self):
		try:
			from docx import Document as DocxDocument
		except ImportError:
			self.skipTest("python-docx não instalado")

		servico = create_test_servico()
		template_names = []

		for idx in range(2):
			with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
				doc = DocxDocument()
				doc.add_paragraph(f"Doc {idx}: {{{{ cliente_nome }}}}")
				doc.save(tmp.name)
				tmp_path = tmp.name

			try:
				file_doc = frappe.get_doc(
					{
						"doctype": "File",
						"file_name": f"template_lote_{idx}.docx",
						"file_url": f"/private/files/template_lote_{idx}.docx",
						"is_private": 1,
					}
				)
				with open(tmp_path, "rb") as f:
					file_doc.content = f.read()
				file_doc.save(ignore_permissions=True)

				template = frappe.get_doc(
					{
						"doctype": "Template Documento",
						"titulo": f"Template Lote {idx} {frappe.generate_hash(length=4)}",
						"tipo_documento": "Contrato",
						"arquivo": file_doc.file_url,
						"habilitado": 1,
					}
				)
				template.insert(ignore_permissions=True)
				template_names.append(template.name)
			finally:
				if os.path.exists(tmp_path):
					os.unlink(tmp_path)

		result = gerar_documentos_em_lote(servico.name, json.dumps(template_names))
		self.assertTrue(result["success"])
		self.assertEqual(result["data"]["total"], 2)
		self.assertEqual(len(result["data"]["gerados"]), 2)
