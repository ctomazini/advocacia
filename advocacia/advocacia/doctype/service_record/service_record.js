
frappe.ui.form.on("Service Record", {
	refresh: function (frm) {
		calcular_totais_atos(frm);
		atualizar_status(frm);
		configurar_botoes_cobranca(frm);
	},
	generate_billing: function (frm) {
		gerar_cobranca_atos(frm);
	},
});

function configurar_botoes_cobranca(frm) {
	if (frm.doc.last_payment && !frm.is_new()) {
		frm.add_custom_button(__("Ver recebimento"), function () {
			frappe.set_route("Form", "Legal Payment", frm.doc.last_payment);
		});
	}

	if (frm.is_new()) {
		return;
	}

	var tem_pendentes = (frm.doc.acts || []).some(function (row) {
		return row.status === "Pendente" && (row.amount || 0) > 0;
	});

	if (tem_pendentes) {
		frm.add_custom_button(__("Sincronizar Cobrança"), function () {
			gerar_cobranca_atos(frm);
		}).addClass("btn-primary-dark");
	}
}

frappe.ui.form.on("Legal Act Item", {
	amount: function (frm) {
		calcular_totais_atos(frm);
	},
	status: function (frm) {
		calcular_totais_atos(frm);
		atualizar_status(frm);
	},
	atos_add: function (frm) {
		calcular_totais_atos(frm);
	},
	atos_remove: function (frm) {
		calcular_totais_atos(frm);
		atualizar_status(frm);
	},
});

function calcular_totais_atos(frm) {
	var pendente = 0;
	var cobrado = 0;
	(frm.doc.acts || []).forEach(function (row) {
		if (row.status === "Pendente") {
			pendente += row.amount || 0;
		} else if (row.status === "Cobrado") {
			cobrado += row.amount || 0;
		}
	});
	frm.set_value("pending_total", pendente);
	frm.set_value("billed_total", cobrado);
	frm.set_value("grand_total", pendente + cobrado);
}

function atualizar_status(frm) {
	if (!frm.doc.acts || frm.doc.acts.length === 0) {
		frm.set_value("status", "Em aberto");
		return;
	}
	var tem_pendente = false;
	var tem_cobrado = false;
	(frm.doc.acts || []).forEach(function (row) {
		if (row.status === "Pendente") tem_pendente = true;
		if (row.status === "Cobrado") tem_cobrado = true;
	});
	if (tem_pendente && tem_cobrado) {
		frm.set_value("status", "Parcialmente cobrado");
	} else if (!tem_pendente && tem_cobrado) {
		frm.set_value("status", "Cobrado");
	} else {
		frm.set_value("status", "Em aberto");
	}
}

function gerar_cobranca_atos(frm) {
	if (frm.is_new()) {
		frappe.msgprint(__("Salve o registro antes de gerar cobrança."));
		return;
	}
	if (!frm.doc.acts || frm.doc.acts.length === 0) {
		frappe.msgprint(__("Não há itens cadastrados."));
		return;
	}

	var pendentes = (frm.doc.acts || []).filter(function (row) {
		return row.status === "Pendente" && (row.amount || 0) > 0 && row.name;
	});
	if (pendentes.length === 0) {
		frappe.msgprint(__("Não há itens pendentes para cobrar."));
		return;
	}

	var vencimento_default =
		frm.doc.billing_due_date || frappe.datetime.add_days(frappe.datetime.get_today(), 30);

	var rows_html = pendentes
		.map(function (row) {
			var desc = row.description || "";
			return (
				"<label style='display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;'>" +
				"<input type='checkbox' class='act-sync-check' data-act-name='" +
				frappe.utils.escape_html(row.name) +
				"' data-act-amount='" +
				(row.amount || 0) +
				"' checked style='margin-top:3px'>" +
				"<span><strong>" +
				frappe.utils.escape_html(row.type || __("Item")) +
				"</strong>" +
				(desc ? " — " + frappe.utils.escape_html(desc) : "") +
				"<br><span style='color:var(--text-muted)'>" +
				format_currency(row.amount || 0) +
				"</span></span></label>"
			);
		})
		.join("");

	var d = new frappe.ui.Dialog({
		title: __("Sincronizar cobrança"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "items_html",
				options:
					"<p style='margin-bottom:12px;color:var(--text-muted)'>" +
					__(
						"Selecione os itens e informe quanto cobrar agora. O valor é alocado na ordem da lista."
					) +
					"</p>" +
					rows_html,
			},
			{
				fieldtype: "Currency",
				fieldname: "billing_amount",
				label: __("Valor a cobrar"),
				reqd: 1,
				default: pendentes.reduce(function (sum, row) {
					return sum + (row.amount || 0);
				}, 0),
			},
			{
				fieldtype: "Date",
				fieldname: "due_date",
				label: __("Vencimento"),
				reqd: 1,
				default: vencimento_default,
			},
			{
				fieldtype: "Small Text",
				fieldname: "sync_hint",
				label: __("Observação"),
				read_only: 1,
				default: __(
					"Itens novos entram no recebimento aberto existente. Um novo recebimento só é criado após receber ou cancelar o anterior."
				),
			},
		],
		primary_action_label: __("Sincronizar"),
		primary_action: function (values) {
			var selected = [];
			var selected_total = 0;
			d.$wrapper.find(".act-sync-check:checked").each(function () {
				selected.push($(this).data("act-name"));
				selected_total += flt($(this).data("act-amount"));
			});

			if (!selected.length) {
				frappe.msgprint(__("Selecione ao menos um item pendente."));
				return;
			}

			if (flt(values.billing_amount) <= 0) {
				frappe.msgprint(__("Informe um valor a cobrar maior que zero."));
				return;
			}

			if (flt(values.billing_amount) - selected_total > 0.009) {
				frappe.msgprint(
					__(
						"Valor a cobrar ({0}) excede o total dos itens selecionados ({1}).",
						[format_currency(values.billing_amount), format_currency(selected_total)]
					)
				);
				return;
			}

			frappe.call({
				method: "advocacia.advocacia.financeiro.sincronizar_pagamento_atos",
				args: {
					registro_name: frm.doc.name,
					due_date: values.due_date,
					act_names: selected,
					billing_amount: values.billing_amount,
				},
				freeze: true,
				freeze_message: __("Sincronizando cobrança..."),
				callback: function (r) {
					if (!r.message) {
						return;
					}
					var msg = r.message;
					var titulo = msg.criado ? __("Recebimento criado") : __("Recebimento atualizado");
					frappe.msgprint({
						title: titulo,
						message:
							(msg.criado
								? __("Recebimento {0} criado com sucesso.", [msg.payment])
								: __("Recebimento {0} atualizado.", [msg.payment])) +
							"<br>" +
							__("Cobrado agora: {0} · Total do recebimento: {1}", [
								format_currency(msg.billing_amount || 0),
								format_currency(msg.total || 0),
							]),
						indicator: "green",
					});
					d.hide();
					frm.reload_doc();
				},
			});
		},
	});

	function atualizar_valor_selecionado() {
		var total = 0;
		d.$wrapper.find(".act-sync-check:checked").each(function () {
			total += flt($(this).data("act-amount"));
		});
		d.set_value("billing_amount", total);
	}

	d.$wrapper.on("change", ".act-sync-check", atualizar_valor_selecionado);
	d.show();
}
