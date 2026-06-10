frappe.provide("advocacia.reports");

advocacia.reports.get_datatable_options = function (options) {
	options.layout = "fluid";
	return options;
};

advocacia.reports.STATUS_BADGE = {
	Recebido: "green",
	Repassado: "blue",
	Pendente: "orange",
	Vencido: "red",
	Cancelado: "gray",
	"Em andamento": "blue",
	Encerrado: "gray",
};

advocacia.reports.TYPE_BADGE = {
	Entrada: "green",
	Saída: "red",
};

advocacia.reports.CURRENCY_FIELDS = [
	"total_vencido",
	"valor_entrada",
	"valor_saida",
	"saldo_acumulado",
	"total_contratado",
	"total_recebido",
	"pending_total",
	"valor_pendente",
	"valor_vencido",
	"total_honorarios",
	"total_custas",
	"lucro_liquido",
	"valor_hora_efetivo",
	"valor_honorarios",
	"valor_hora",
];

advocacia.reports.badge = function (text, color) {
	if (!text) return "";
	return `<span class="adv-report-badge adv-report-badge--${color || "gray"}">${frappe.utils.escape_html(
		text
	)}</span>`;
};

advocacia.reports.format_currency = function (value) {
	return frappe.format(value || 0, { fieldtype: "Currency", currency: "BRL" });
};

advocacia.reports.get_office_header_html = function () {
	const office = (frappe.boot && frappe.boot.adv_office) || {};
	const parts = [];
	if (office.logo_url) {
		parts.push(
			`<div class="adv-rpt-desk-header__logo"><img src="${frappe.utils.escape_html(
				office.logo_url
			)}" alt=""></div>`
		);
	}
	parts.push(`<div class="adv-rpt-desk-header__office"><strong>${frappe.utils.escape_html(
		office.company_name || __("Escritório de Advocacia")
	)}</strong>`);
	if (office.cnpj) {
		parts.push(
			`<div class="muted">CNPJ ${frappe.utils.escape_html(office.cnpj)}</div>`
		);
	}
	if (office.oab) {
		parts.push(`<div class="muted">OAB ${frappe.utils.escape_html(office.oab)}</div>`);
	}
	if (office.lawyer_name) {
		parts.push(
			`<div class="muted">${frappe.utils.escape_html(office.lawyer_name)}</div>`
		);
	}
	parts.push("</div>");
	return `<div class="adv-rpt-desk-header">${parts.join("")}</div>`;
};

advocacia.reports.get_status_badge = function (status) {
	if (!status) return "";
	const plain = String(status).replace(/[^\w\sÀ-ú%-]/g, "").trim();
	let color = advocacia.reports.STATUS_BADGE[plain];
	if (!color) {
		if (plain.indexOf("Inadimplente") !== -1) color = "red";
		else if (plain.indexOf("Em dia") !== -1) color = "orange";
		else if (plain.indexOf("Quitado") !== -1) color = "green";
		else color = "gray";
	}
	return advocacia.reports.badge(status, color);
};

advocacia.reports.withCommonFormatter = function (customFormatter) {
	const wrapped = function (value, row, column, data, default_formatter) {
		let formatted = default_formatter(value, row, column, data);

		if (column.fieldname === "type" && row.type) {
			const color =
				advocacia.reports.TYPE_BADGE[row.type] ||
				(row.type === __("Entrada") ? "green" : row.type === __("Saída") ? "red" : "gray");
			formatted = advocacia.reports.badge(row.type, color);
		} else if (column.fieldname === "situacao_financeira" && row.situacao_financeira) {
			formatted = advocacia.reports.get_status_badge(row.situacao_financeira);
		} else if (column.fieldname === "status" && row.status) {
			formatted = advocacia.reports.get_status_badge(row.status);
		} else if (advocacia.reports.CURRENCY_FIELDS.includes(column.fieldname)) {
			let tone = "";
			if (
				(column.fieldname === "total_vencido" || column.fieldname === "valor_vencido") &&
				flt(row[column.fieldname]) > 0
			) {
				tone = "var(--red-600)";
			} else if (column.fieldname === "lucro_liquido" && flt(row.lucro_liquido) < 0) {
				tone = "var(--red-600)";
			} else if (
				(column.fieldname === "total_recebido" || column.fieldname === "valor_entrada") &&
				flt(row[column.fieldname]) > 0
			) {
				tone = "var(--green-600)";
			}
			formatted = tone
				? `<span class="adv-rpt-num" style="color:${tone}">${formatted}</span>`
				: `<span class="adv-rpt-num">${formatted}</span>`;
		} else if (column.fieldname === "description" && row.description) {
			const esc = frappe.utils.escape_html(row.description);
			formatted = `<span class="adv-rpt-desc" title="${esc}">${esc}</span>`;
		}

		if (customFormatter) {
			formatted = customFormatter(value, row, column, data, () => formatted);
		}

		return formatted;
	};
	wrapped._adv_common_wrapped = true;
	return wrapped;
};

advocacia.reports.enhanceReportSettings = function (reportName) {
	const settings = frappe.query_reports[reportName];
	if (!settings || settings._adv_visual_enhanced) {
		return;
	}

	const existingFormatter = settings.formatter;
	if (existingFormatter?._adv_common_wrapped) {
		settings._adv_visual_enhanced = true;
		return;
	}

	settings.formatter = advocacia.reports.withCommonFormatter(
		existingFormatter
			? function (value, row, column, data, default_formatter) {
					return existingFormatter(value, row, column, data, default_formatter);
				}
			: null
	);

	if (!settings.get_chart_data) {
		settings.get_chart_data = function (chart) {
			return chart;
		};
	}

	settings._adv_visual_enhanced = true;
};

advocacia.reports.ADV_REPORTS = [
	"inadimplencia",
	"fluxo_de_caixa",
	"honorarios_por_cliente",
	"carteira_ativa",
	"produtividade",
	"horas_por_servico",
];

function advocacia_patch_query_report() {
	if (advocacia.reports._query_report_patched || !frappe.views?.QueryReport) {
		return;
	}
	advocacia.reports._query_report_patched = true;

	const proto = frappe.views.QueryReport.prototype;
	const render_datatable = proto.render_datatable;
	const refresh = proto.refresh;

	proto.render_datatable = function () {
		this.report_settings = this.report_settings || {};
		if (!this.report_settings.get_datatable_options) {
			this.report_settings.get_datatable_options = advocacia.reports.get_datatable_options;
		}
		render_datatable.call(this);
		if (this.datatable?.style?.setDimensions) {
			this.datatable.style.setDimensions();
		}
	};

	proto.refresh = function (...args) {
		if (this.report_name && advocacia.reports.ADV_REPORTS.includes(this.report_name)) {
			advocacia.reports.enhanceReportSettings(this.report_name);
			this.page?.main?.addClass?.("adv-report-page");
		}
		return refresh.apply(this, args);
	};
}

advocacia_patch_query_report();
$(document).on("app_ready", advocacia_patch_query_report);
