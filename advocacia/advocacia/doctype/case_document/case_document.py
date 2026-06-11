import frappe
from frappe import _
from frappe.model.document import Document

from advocacia.advocacia.case_document_naming import compose_case_document_title


class CaseDocument(Document):
	def validate(self):
		self._sync_client_from_case()
		self._compose_title()
		self._validate_deadline_case()

	def _sync_client_from_case(self):
		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")

	def _compose_title(self):
		if not self.legal_case or not self.category:
			return
		self.title = compose_case_document_title(
			self.category,
			self.legal_case,
			self.version_label,
		)

	def _validate_deadline_case(self):
		if not self.related_deadline:
			return

		deadline_case = frappe.db.get_value("Deadline", self.related_deadline, "legal_case")
		if deadline_case and deadline_case != self.legal_case:
			frappe.throw(
				_("O prazo {0} pertence ao serviço {1}, não ao serviço {2}.").format(
					self.related_deadline,
					deadline_case,
					self.legal_case,
				),
				title=_("Prazo inválido"),
			)
