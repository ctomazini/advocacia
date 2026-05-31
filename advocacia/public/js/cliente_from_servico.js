(function () {
	const DOCTYPES_COM_SERVICO = [
		"Tarefa",
		"Audiencia",
		"Controle de Prazos",
		"Comunicacao",
		"Registro de Horas",
		"Registro de Atos",
		"Acordo de Honorarios Processuais",
		"Custa Processual",
		"Pagamento",
	];

	function fetch_cliente_from_servico(servico, callback) {
		if (!servico) {
			callback("");
			return;
		}
		frappe.db.get_value("Servico", servico, "cliente", (value) => {
			callback((value && value.cliente) || "");
		});
	}

	function sync_cliente_no_form(frm) {
		if (!frm.fields_dict.cliente || !frm.fields_dict.servico) {
			return;
		}
		if (!frm.doc.servico) {
			if (frm.doc.cliente) {
				frm.set_value("cliente", "");
			}
			return;
		}
		if (frm.doc.cliente) {
			return;
		}
		fetch_cliente_from_servico(frm.doc.servico, (cliente) => {
			if (cliente && frm.doc.cliente !== cliente) {
				frm.set_value("cliente", cliente);
			}
		});
	}

	DOCTYPES_COM_SERVICO.forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			servico(frm) {
				fetch_cliente_from_servico(frm.doc.servico, (cliente) => {
					frm.set_value("cliente", cliente);
				});
			},
			refresh(frm) {
				sync_cliente_no_form(frm);
			},
		});
	});

	if (!frappe.ui.form.QuickEntryForm) {
		return;
	}

	const QuickEntryForm = frappe.ui.form.QuickEntryForm;
	const original_open_doc = QuickEntryForm.prototype.open_doc;
	const original_render_dialog = QuickEntryForm.prototype.render_dialog;

	function vincular_servico_no_quick_entry(me) {
		if (!DOCTYPES_COM_SERVICO.includes(me.doctype)) {
			return;
		}
		const servico_field = me.fields_dict && me.fields_dict.servico;
		if (!servico_field) {
			return;
		}

		const atualizar_cliente = () => {
			const servico = me.get_value("servico");
			fetch_cliente_from_servico(servico, (cliente) => {
				me.doc.cliente = cliente || "";
			});
		};

		servico_field.$input.on("change", atualizar_cliente);
		if (me.doc.servico && !me.doc.cliente) {
			atualizar_cliente();
		}
	}

	QuickEntryForm.prototype.render_dialog = function () {
		original_render_dialog.call(this);
		vincular_servico_no_quick_entry(this);
	};

	QuickEntryForm.prototype.open_doc = function (set_hooks) {
		const me = this;
		if (
			DOCTYPES_COM_SERVICO.includes(me.doctype) &&
			me.doc.servico &&
			!me.doc.cliente
		) {
			fetch_cliente_from_servico(me.doc.servico, (cliente) => {
				if (cliente) {
					me.doc.cliente = cliente;
				}
				original_open_doc.call(me, set_hooks);
			});
			return;
		}
		original_open_doc.call(me, set_hooks);
	};
})();
