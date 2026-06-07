/* eslint-disable */
(function (AP) {
	var U = advocacia.painel.utils;

	AP.bind_painel_filters = function ($root, page) {
		$root.off("click.painelFilters");
		$root.on("click.painelFilters", ".painel-periodo-btn", function (e) {
			e.preventDefault();
			var dias = U.cint($(this).attr("data-periodo"));
			if (!page || dias === page.painel_periodo) return;
			page.painel_periodo = dias;
			$root.find(".painel-periodo-btn").removeClass("active");
			$(this).addClass("active");
			AP.load(page, { soft: true, period: true });
		});
		$root.on("click.painelFilters", ".painel-linhas-btn", function (e) {
			e.preventDefault();
			var list_key = $(this).attr("data-list");
			var linhas = U.cint($(this).attr("data-linhas"));
			if (!page || !list_key) return;
			if (!page.painel_list_limits) {
				page.painel_list_limits = U.painel_default_list_limits();
			}
			if (linhas === page.painel_list_limits[list_key]) return;
			page.painel_list_limits[list_key] = linhas;
			var $group = $(this).closest(".painel-linhas-filters");
			$group.find(".painel-linhas-btn").removeClass("active");
			$(this).addClass("active");
			AP.load(page, { soft: true, section: list_key });
		});
	};

	AP.bind_atencao_routes = function ($root, page) {
		$root.off("click.painelAtencao");
		$root.on("click.painelAtencao", ".painel-atencao-card[data-atencao-route]", function () {
			var hoje = frappe.datetime.get_today();
			var amanha = frappe.datetime.add_days(hoje, 1);
			var tres_dias = frappe.datetime.add_days(hoje, 3);
			var periodo_fim = U.painel_periodo_fim(page);
			var mes_inicio = frappe.datetime.month_start(hoje);
			var mes_fim = frappe.datetime.month_end(hoje);
			var key = $(this).attr("data-atencao-route");

			var routes = {
				audiencias_hoje: function () {
					U.painel_goto_list("Hearing", [
						["data_hora", "between", [hoje + " 00:00:00", hoje + " 23:59:59"]],
					]);
				},
				audiencias_amanha: function () {
					U.painel_goto_list("Hearing", [
						["data_hora", "between", [amanha + " 00:00:00", amanha + " 23:59:59"]],
					]);
				},
				audiencias_periodo: function () {
					U.painel_goto_list("Hearing", [
						["data_hora", "between", [hoje + " 00:00:00", periodo_fim + " 23:59:59"]],
					]);
				},
				prazos_vencidos: function () {
					U.painel_goto_list("Deadline", [
						["status", "=", "Pendente"],
						["data_prazo", "<", hoje],
					]);
				},
				prazos_proximos: function () {
					U.painel_goto_list("Deadline", [
						["status", "=", "Pendente"],
						["data_prazo", "between", [hoje, tres_dias]],
					]);
				},
				prazos_criticos: function () {
					U.painel_goto_list("Deadline", [
						["status", "=", "Pendente"],
						["data_prazo", "<=", tres_dias],
					]);
				},
				tarefas_atrasadas: function () {
					U.painel_goto_list("Legal Task", [
						["status", "in", ["Pendente", "Em Andamento"]],
						["data_limite", "<", hoje],
					]);
				},
				tarefas_pendentes: function () {
					U.painel_goto_list("Legal Task", [["status", "in", ["Pendente", "Em Andamento"]]]);
				},
				parcelas_vencidas: function () {
					U.painel_goto_list("Legal Payment", [["status", "=", "Vencido"]]);
				},
				pagamentos_periodo: function () {
					U.painel_goto_list("Legal Payment", [
						["status", "=", "Pendente"],
						["data_vencimento", "between", [hoje, periodo_fim]],
					]);
				},
				recebimentos_periodo: function () {
					U.painel_goto_list("Legal Payment", [
						["status", "in", ["Recebido", "Repassado"]],
						["data_recebimento", "between", [hoje, periodo_fim]],
					]);
				},
				receita_mes: function () {
					U.painel_goto_list("Legal Payment", [
						["status", "in", ["Recebido", "Repassado"]],
						["data_recebimento", "between", [mes_inicio, mes_fim]],
					]);
				},
				honorarios_ativos: function () {
					U.painel_goto_list("Fee Agreement", [["status", "=", "Vigente"]]);
				},
				horas: function () {
					U.painel_goto_list("Time Entry", [["data", "between", [hoje, periodo_fim]]]);
				},
				clientes: function () {
					U.painel_goto_list("Client", []);
				},
				taxa_recebimento: function () {
					frappe.set_route("query-report", "inadimplencia");
				},
				processos_ativos: function () {
					U.painel_goto_list("Legal Case", [["status", "=", "Em andamento"]]);
				},
				custas_abertas: function () {
					U.painel_goto_list("Court Cost", [
						["status", "in", ["Pendente", "Pago"]],
						["repassar_cliente", "=", 1],
					]);
				},
				despesas_mes: function () {
					U.painel_goto_list("Office Expense", [
						["data_vencimento", "between", [mes_inicio, mes_fim]],
					]);
				},
			};

			if (routes[key]) routes[key]();
		});
	};
})(advocacia.painel);

$(document).on("click", ".painel-timeline-item[data-dt], .painel-tl-item[data-dt]", function (e) {
	if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
	var dt = $(this).attr("data-dt");
	var dn = $(this).attr("data-dn");
	if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-prox-card[data-dt], .painel-prox-body[data-dt]", function (e) {
	if ($(e.target).closest(".painel-btn-entrar").length) return;
	var dt = $(this).attr("data-dt");
	var dn = $(this).attr("data-dn");
	if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", "[data-route-calendar]", function (e) {
	e.stopPropagation();
	frappe.set_route("List", "Hearing", "Calendar");
});

$(document).on("click", ".painel-schedule-item[data-dt], .painel-com-item[data-dt]", function (e) {
	if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
	var dt = $(this).attr("data-dt");
	var dn = $(this).attr("data-dn");
	if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-action-chip", function () {
	var dt = $(this).attr("data-new-dt");
	if (dt) frappe.new_doc(dt);
});

$(document).on("click", ".painel-section-link[data-scroll]", function () {
	advocacia.painel.utils.scroll_painel_section($(this).attr("data-scroll"));
});

$(document).on("click", "[data-route-list]", function (e) {
	e.stopPropagation();
	var dt = $(this).attr("data-route-list");
	if (dt) advocacia.painel.utils.painel_goto_list(dt, []);
});

$(document).on("click", ".painel-schedule-card[data-dt]", function (e) {
	if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
	var dt = $(this).attr("data-dt");
	var dn = $(this).attr("data-dn");
	if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-op-item[data-dt]", function (e) {
	if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
	var dt = $(this).attr("data-dt");
	var dn = $(this).attr("data-dn");
	if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-parcela-critica", function (e) {
	if ($(e.target).closest(".painel-btn-recebida").length) return;
	var acordo = $(this).attr("data-acordo");
	if (acordo) frappe.set_route("Form", "Fee Agreement", acordo);
});

$(document).on("click", ".painel-row-acordo", function (e) {
	if ($(e.target).closest(".painel-btn-recebida").length) return;
	var acordo = $(this).attr("data-acordo");
	if (acordo) frappe.set_route("Form", "Fee Agreement", acordo);
});

$(document).on("click", ".painel-btn-recebida", function (e) {
	e.stopPropagation();
	var btn = $(this);
	var pagamento = btn.attr("data-pagamento") || btn.attr("data-parcela");
	if (!pagamento) return;

	frappe.confirm(__("Marcar pagamento como recebido hoje?"), function () {
		btn.prop("disabled", true).text("...");
		frappe
			.xcall("advocacia.advocacia.painel_api.marcar_parcela_recebida", {
				parcela_name: pagamento,
			})
			.then(function () {
				frappe.show_alert({
					message: __("Legal Payment marcado como Recebido"),
					indicator: "green",
				});
				var page =
					(frappe.pages.painel && frappe.pages.painel.page) ||
					(cur_page && cur_page.page ? cur_page.page : null);
				if (page && advocacia.painel.load) {
					advocacia.painel.load(page);
				}
			})
			.catch(function (err) {
				btn.prop("disabled", false).text("✓ " + __("Recebido"));
				frappe.msgprint(err.message || __("Erro ao marcar parcela"));
			});
	});
});
