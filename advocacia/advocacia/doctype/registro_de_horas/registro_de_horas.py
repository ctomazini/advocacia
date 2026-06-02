import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class RegistrodeHoras(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")

		if self.duracao_minutos is None:
			self.duracao_minutos = 0

		if self.hora_inicio and self.hora_fim and not self.duracao_minutos:
			diff = time_diff_in_seconds(self.hora_fim, self.hora_inicio)
			self.duracao_minutos = max(0, int(diff / 60))

		self.duracao_horas = round((self.duracao_minutos or 0) / 60, 2)
		recompor_titulo_se_vazio(self)

		if self.timer_ativo and self.has_value_changed("duracao_minutos"):
			frappe.throw(
				_(
					"Não é possível editar a duração manualmente enquanto o timer está ativo. Pare o timer primeiro."
				)
			)

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	@frappe.whitelist()
	def iniciar_timer(self):
		self.check_permission("write")
		if self.timer_ativo:
			frappe.throw(_("Timer já está em execução para este registro."))

		self.timer_inicio = now_datetime()
		self.timer_ativo = 1
		self.save()

		return {"timer_inicio": str(self.timer_inicio)}

	@frappe.whitelist()
	def parar_timer(self):
		self.check_permission("write")
		if not self.timer_ativo:
			frappe.throw(_("Nenhum timer ativo para este registro."))

		elapsed_seconds = time_diff_in_seconds(now_datetime(), self.timer_inicio)
		elapsed_minutes = max(0, int(round(elapsed_seconds / 60)))

		current = self.duracao_minutos or 0
		self.duracao_minutos = current + elapsed_minutes
		self.duracao_horas = round(self.duracao_minutos / 60, 2)

		self.timer_inicio = None
		self.timer_ativo = 0
		self.save()

		return {
			"duracao_minutos": self.duracao_minutos,
			"duracao_horas": self.duracao_horas,
			"elapsed_seconds": elapsed_seconds,
		}


@frappe.whitelist()
def get_timer_ativo_usuario():
	"""Retorna o registro com timer ativo do usuário logado, se existir."""
	if frappe.session.user == "Guest":
		return None

	if not frappe.has_permission("Registro de Horas", "read"):
		return None

	if not frappe.db.table_exists("Registro de Horas"):
		return None

	user = frappe.session.user
	rows = frappe.get_all(
		"Registro de Horas",
		filters={"timer_ativo": 1},
		fields=["name", "timer_inicio", "atividade", "servico", "responsavel", "owner"],
		order_by="modified desc",
		limit_page_length=20,
	)

	for row in rows:
		if row.responsavel and row.responsavel != user:
			continue
		if not row.responsavel and row.owner != user:
			continue
		return {
			"name": row.name,
			"timer_inicio": str(row.timer_inicio),
			"atividade": row.atividade or row.name,
			"servico": row.servico or "",
		}

	return None
