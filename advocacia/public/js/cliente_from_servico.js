(function () {
	const DOCTYPES_COM_SERVICO = [
		"Legal Task",
		"Hearing",
		"Deadline",
		"Case Communication",
		"Time Entry",
		"Service Record",
		"Fee Agreement",
		"Court Cost",
		"Legal Payment",
	];

	function fetch_cliente_from_servico(servico, callback) {
		if (!servico) {
			callback("");
			return;
		}
		frappe.db.get_value("Legal Case", servico, "client", (value) => {
			callback((value && value.client) || "");
		});
	}

	function sync_cliente_no_form(frm) {
		if (!frm.fields_dict.client || !frm.fields_dict.legal_case) {
			return;
		}
		if (!frm.doc.legal_case) {
			if (frm.doc.client) {
				frm.set_value("client", "");
			}
			return;
		}
		if (frm.doc.client) {
			return;
		}
		fetch_cliente_from_servico(frm.doc.legal_case, (cliente) => {
			if (cliente && frm.doc.client !== cliente) {
				frm.set_value("client", cliente);
			}
		});
	}

	DOCTYPES_COM_SERVICO.forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			servico(frm) {
				fetch_cliente_from_servico(frm.doc.legal_case, (cliente) => {
					frm.set_value("client", cliente);
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
		const servico_field = me.fields_dict && me.fields_dict.legal_case;
		if (!servico_field) {
			return;
		}

		const atualizar_cliente = () => {
			const servico = me.get_value("legal_case");
			fetch_cliente_from_servico(servico, (cliente) => {
				me.doc.client = cliente || "";
			});
		};

		servico_field.$input.on("change", atualizar_cliente);
		if (me.doc.legal_case && !me.doc.client) {
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
			me.doc.legal_case &&
			!me.doc.client
		) {
			fetch_cliente_from_servico(me.doc.legal_case, (cliente) => {
				if (cliente) {
					me.doc.client = cliente;
				}
				original_open_doc.call(me, set_hooks);
			});
			return;
		}
		original_open_doc.call(me, set_hooks);
	};
})();
