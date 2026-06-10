import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class TimeEntry(Document):
	def validate(self):
		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")

		if self.duration_minutes is None:
			self.duration_minutes = 0

		if self.start_time and self.end_time and not self.duration_minutes:
			diff = time_diff_in_seconds(self.end_time, self.start_time)
			self.duration_minutes = max(0, int(diff / 60))

		self.duration_hours = round((self.duration_minutes or 0) / 60, 2)
		self._compor_titulo()

		if self.timer_active and self.has_value_changed("duration_minutes"):
			frappe.throw(
				_(
					"Não é possível editar a duração manualmente enquanto o timer está ativo. Pare o timer primeiro."
				)
			)

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	@frappe.whitelist()
	def iniciar_timer(self) -> dict:
		frappe.has_permission("Time Entry", "write", doc=self, throw=True)
		if self.timer_active:
			frappe.throw(_("Timer já está em execução para este registro."))

		self.timer_start = now_datetime()
		self.timer_active = 1
		self.save()

		return {"timer_start": str(self.timer_start)}

	@frappe.whitelist()
	def parar_timer(self) -> dict:
		frappe.has_permission("Time Entry", "write", doc=self, throw=True)
		if not self.timer_active:
			frappe.throw(_("Nenhum timer ativo para este registro."))

		elapsed_seconds = time_diff_in_seconds(now_datetime(), self.timer_start)
		elapsed_minutes = max(0, int(round(elapsed_seconds / 60)))

		current = self.duration_minutes or 0
		self.duration_minutes = current + elapsed_minutes
		self.duration_hours = round(self.duration_minutes / 60, 2)

		self.timer_start = None
		self.timer_active = 0
		self.save()

		return {
			"duration_minutes": self.duration_minutes,
			"duration_hours": self.duration_hours,
			"elapsed_seconds": elapsed_seconds,
		}


@frappe.whitelist()
def get_timer_ativo_usuario() -> dict | None:
	"""Retorna o registro com timer ativo do usuário logado, se existir."""
	if frappe.session.user == "Guest":
		return None

	if not frappe.has_permission("Time Entry", "read"):
		return None

	if not frappe.db.table_exists("Time Entry"):
		return None

	user = frappe.session.user
	rows = frappe.get_all(
		"Time Entry",
		filters={"timer_active": 1},
		fields=["name", "timer_start", "activity", "legal_case", "responsible", "owner"],
		order_by="modified desc",
		limit_page_length=20,
	)

	for row in rows:
		if row.responsible and row.responsible != user:
			continue
		if not row.responsible and row.owner != user:
			continue
		return {
			"name": row.name,
			"timer_start": str(row.timer_start),
			"activity": row.activity or row.name,
			"legal_case": row.legal_case or "",
		}

	return None
