import frappe

# Nomes exibidos na UI (desk, breadcrumbs, títulos de lista). IDs internos permanecem EN.
DOCTYPE_LABELS = {
	"Legal Case": "Serviços",
	"Client": "Clientes",
	"Legal Payment": "Pagamentos",
	"Legal Task": "Tarefas",
	"Time Entry": "Registro de Horas",
	"Service Record": "Cobrança de serviços",
	"Hearing": "Audiências",
	"Case Communication": "Comunicações",
	"Court Cost": "Custas Processuais",
	"Office Expense": "Despesas",
	"Fee Agreement": "Honorários",
	"Deadline": "Prazos",
	"Document Template": "Modelos Word",
	"Document Kit": "Kits de Documentos",
	"Office Settings": "Configuração do Escritório",
	"Jurisdiction": "Comarca",
	"Court Branch": "Vara",
	"Court": "Tribunal",
	"Case Phase": "Fase Processual",
	"Document Category": "Categoria de Documento",
	"Case Document": "Documentos do Processo",
	"Fee Installment": "Parcelas de Honorários",
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
