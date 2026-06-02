import frappe

DOCTYPE_LABELS = {
	"Acordo de Honorarios Processuais": "Honorários",
	"Controle de Prazos": "Prazos",
	"Template Documento": "Documentos",
	"Kit de Documentos": "Kits de Documentos",
	"Configuracao do Escritorio": "Configuração do Escritório",
	"Registro de Atos": "Registro de Atos",
}


def ensure_doctype_translations():
	"""Traduz nomes de DocType exibidos na UI (nome interno permanece inalterado)."""
	languages = ["pt", "pt-BR"]
	for source, translated in DOCTYPE_LABELS.items():
		for lang in languages:
			if not frappe.db.exists("Language", lang):
				continue
			try:
				if frappe.db.exists(
					"Translation",
					{"source_text": source, "language": lang, "translated_text": translated},
				):
					continue
				if frappe.db.exists("Translation", {"source_text": source, "language": lang}):
					frappe.db.set_value(
						"Translation",
						{"source_text": source, "language": lang},
						"translated_text",
						translated,
						update_modified=True,
					)
					continue
				frappe.get_doc(
					{
						"doctype": "Translation",
						"language": lang,
						"source_text": source,
						"translated_text": translated,
						"contributed": 0,
					}
				).insert(ignore_permissions=True)  # setup: seed de traduções como Administrator
			except frappe.DoesNotExistError:
				pass
			except Exception:
				frappe.log_error(
					title="Advocacia translations seed",
					message=frappe.get_traceback(),
				)
	frappe.db.commit()
	frappe.clear_cache()
