
frappe.ui.form.on("Service Record", {
	refresh: function (frm) {
		calcular_totais_atos(frm);
		atualizar_status(frm);
		configurar_botoes_cobranca(frm);
	},
	gerar_cobranca: function (frm) {
		gerar_cobranca_atos(frm);
	},
});

function configurar_botoes_cobranca(frm) {
	if (frm.doc.last_payment && !frm.is_new()) {
		frm.add_custom_button(__("Ver Legal Payment"), function () {
			frappe.set_route("Form", "Legal Payment", frm.doc.last_payment);
		});
	}

	if (frm.is_new()) {
		return;
	}

	var tem_pendentes = (frm.doc.acts || []).some(function (row) {
		return row.status === "Pendente" && (row.valor || 0) > 0;
	});

	if (tem_pendentes) {
		frm.add_custom_button(__("Sincronizar Cobrança"), function () {
			gerar_cobranca_atos(frm);
		}).addClass("btn-primary-dark");
	}
}

frappe.ui.form.on("Legal Act Item", {
	valor: function (frm) {
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
			pendente += row.valor || 0;
		} else if (row.status === "Cobrado") {
			cobrado += row.valor || 0;
		}
	});
	frm.set_value("total_pendente", pendente);
	frm.set_value("total_cobrado", cobrado);
	frm.set_value("total_geral", pendente + cobrado);
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
		frappe.msgprint(__("Não há atos cadastrados."));
		return;
	}
	var pendentes = [];
	(frm.doc.acts || []).forEach(function (row) {
		if (row.status === "Pendente" && (row.valor || 0) > 0) {
			pendentes.push(row);
		}
	});
	if (pendentes.length === 0) {
		frappe.msgprint(__("Não há atos pendentes para cobrar."));
		return;
	}
	var total = 0;
	var descricao_itens = [];
	pendentes.forEach(function (row) {
		total += row.valor || 0;
		descricao_itens.push(
			(row.tipo || __("Ato")) +
				": " +
				(row.description || row.descricao || "") +
				" (R$ " +
				(row.valor || 0).toFixed(2) +
				")"
		);
	});

	var vencimento_default =
		frm.doc.data_vencimento_cobranca || frappe.datetime.add_days(frappe.datetime.get_today(), 30);

	frappe.confirm(
		"<strong>" +
			__("Sincronizar cobrança com {0} ato(s) pendente(s)?", [pendentes.length]) +
			"</strong><br><br>" +
			descricao_itens.join("<br>") +
			"<br><br><strong>" +
			__("Total: R$ {0}", [total.toFixed(2)]) +
			"</strong><br><small>" +
			__(
				"Atos novos entram no pagamento aberto existente. Um novo pagamento só é criado após receber ou cancelar o anterior."
			) +
			"</small>",
		function () {
			frappe.call({
				method: "advocacia.advocacia.financeiro.sincronizar_pagamento_atos",
				args: {
					registro_name: frm.doc.name,
					data_vencimento: vencimento_default,
				},
				freeze: true,
				freeze_message: __("Sincronizando cobrança..."),
				callback: function (r) {
					if (!r.message) return;
					var msg = r.message;
					var titulo = msg.criado ? __("Legal Payment criado") : __("Legal Payment atualizado");
					frappe.msgprint({
						title: titulo,
						message:
							(msg.criado
								? __("Legal Payment {0} criado com sucesso.", [msg.payment])
								: __("Legal Payment {0} atualizado.", [msg.payment])) +
							"<br>" +
							__("Total: R$ {0} · {1} ato(s)", [
								(msg.total || 0).toFixed(2),
								msg.qtd_atos || 0,
							]),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		}
	);
}
