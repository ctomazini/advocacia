const AdvocaciaMasks = {
	onlyDigits(v) {
		return (v || "").replace(/\D/g, "");
	},

	applyCPF(v) {
		v = this.onlyDigits(v).substring(0, 11);
		if (v.length > 9) return v.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
		if (v.length > 6) return v.replace(/(\d{3})(\d{3})(\d{0,3})/, "$1.$2.$3");
		if (v.length > 3) return v.replace(/(\d{3})(\d{0,3})/, "$1.$2");
		return v;
	},

	applyCNPJ(v) {
		v = this.onlyDigits(v).substring(0, 14);
		if (v.length > 12)
			return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
		if (v.length > 8) return v.replace(/(\d{2})(\d{3})(\d{3})(\d{0,4})/, "$1.$2.$3/$4");
		if (v.length > 5) return v.replace(/(\d{2})(\d{3})(\d{0,3})/, "$1.$2.$3");
		if (v.length > 2) return v.replace(/(\d{2})(\d{0,3})/, "$1.$2");
		return v;
	},

	applyPhone(v) {
		v = this.onlyDigits(v).substring(0, 11);
		if (v.length > 10) return v.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
		if (v.length > 6) return v.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
		if (v.length > 2) return v.replace(/(\d{2})(\d{0,5})/, "($1) $2");
		return v;
	},

	applyCEP(v) {
		v = this.onlyDigits(v).substring(0, 8);
		if (v.length > 5) return v.replace(/(\d{5})(\d{0,3})/, "$1-$2");
		return v;
	},

	applyCNJ(v) {
		v = this.onlyDigits(v).substring(0, 20);
		if (v.length > 13)
			return v.replace(
				/(\d{7})(\d{2})(\d{4})(\d{1})(\d{2})(\d{0,4})/,
				"$1-$2.$3.$4.$5.$6"
			);
		if (v.length > 12)
			return v.replace(/(\d{7})(\d{2})(\d{4})(\d{1})(\d{0,2})/, "$1-$2.$3.$4.$5");
		if (v.length > 9) return v.replace(/(\d{7})(\d{2})(\d{0,4})/, "$1-$2.$3");
		if (v.length > 7) return v.replace(/(\d{7})(\d{0,2})/, "$1-$2");
		return v;
	},

	listFormatters: {
		cpf(value) {
			return AdvocaciaMasks.applyCPF(value) || "";
		},
		cnpj(value) {
			return AdvocaciaMasks.applyCNPJ(value) || "";
		},
		phone(value) {
			return AdvocaciaMasks.applyPhone(value) || "";
		},
		cep(value) {
			return AdvocaciaMasks.applyCEP(value) || "";
		},
	},

	_bindInput($input, maskFn) {
		if (!$input || !$input.length) return;

		if ($.fn.inputmask) {
			$input.off("input.advocacia_mask");
			return;
		}

		$input.off("input.advocacia_mask").on("input.advocacia_mask", function () {
			const val = $(this).val();
			const masked = maskFn.call(AdvocaciaMasks, val);
			if (val !== masked) {
				const pos = this.selectionStart;
				const diff = masked.length - val.length;
				$(this).val(masked);
				this.setSelectionRange(pos + diff, pos + diff);
			}
		});
	},

	_inputmaskPattern(tipo) {
		const patterns = {
			cpf: "999.999.999-99",
			cnpj: "99.999.999/9999-99",
			cnj: "9999999-99.9999.9.99.9999",
			mobile: "(99) 99999-9999",
			fixo: "(99) 9999-9999",
			phone: "(99) 99999-9999",
			cep: "99999-999",
		};
		return patterns[tipo] || "";
	},

	_refreshDisplay(field, maskFn) {
		if (!field || !field.$input) return;
		const raw = field.get_value && field.get_value();
		if (!raw) return;
		const masked = maskFn.call(this, raw);
		if (field.$input.val() !== masked) {
			field.$input.val(masked);
		}
	},

	bindMask(frm, fieldname, maskFn, inputmaskTipo) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !field.$input) return;

		field.$input.off(".advocacia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}

		if ($.fn.inputmask && inputmaskTipo) {
			field.$input.inputmask(this._inputmaskPattern(inputmaskTipo));
		} else {
			this._bindInput(field.$input, maskFn);
		}

		this._refreshDisplay(field, maskFn);
	},

	unbindMask(frm, fieldname) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !field.$input) return;
		field.$input.off(".advocacia_mask input.advocacia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}
	},

	formatFormField(frm, fieldname, maskFn) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !frm.doc[fieldname]) return;
		this._refreshDisplay(field, maskFn);
	},

	formatChildField(cdt, cdn, fieldname, maskFn) {
		const row = locals[cdt] && locals[cdt][cdn];
		if (!row || !row[fieldname]) return;
		const masked = maskFn.call(this, row[fieldname]);
		if (row[fieldname] !== masked) {
			frappe.model.set_value(cdt, cdn, fieldname, masked);
		}
	},

	setupGridMaskFormatters(frm, tableFieldname, specs) {
		const grid = frm.fields_dict[tableFieldname] && frm.fields_dict[tableFieldname].grid;
		if (!grid) return;

		specs.forEach(({ fieldname, maskFn }) => {
			const df = grid.get_docfield(fieldname);
			if (!df) return;
			df.formatter = (value) => {
				if (!value) return "";
				return frappe.utils.escape_html(maskFn.call(AdvocaciaMasks, value));
			};
		});
		grid.refresh();
	},

	setupClientForm(frm) {
		if (!window.AdvocaciaMasks) return;

		if (frm.doc.person_type === "Pessoa Física") {
			this.bindMask(frm, "cpf", this.applyCPF, "cpf");
			this.unbindMask(frm, "cnpj");
			this.unbindMask(frm, "representative_cpf");
		} else if (frm.doc.person_type === "Pessoa Jurídica") {
			this.bindMask(frm, "cnpj", this.applyCNPJ, "cnpj");
			this.bindMask(frm, "representative_cpf", this.applyCPF, "cpf");
			this.unbindMask(frm, "cpf");
		}

		["cpf", "cnpj", "representative_cpf"].forEach((fieldname) => {
			if (!frm.doc[fieldname]) return;
			const fn = fieldname === "cnpj" ? this.applyCNPJ : this.applyCPF;
			this.formatFormField(frm, fieldname, fn);
		});

		this.setupGridMaskFormatters(frm, "contacts", [
			{ fieldname: "phone", maskFn: this.applyPhone },
			{ fieldname: "mobile", maskFn: this.applyPhone },
		]);
		this.setupGridMaskFormatters(frm, "addresses", [{ fieldname: "cep", maskFn: this.applyCEP }]);
	},

	setupOfficeSettingsForm(frm) {
		if (!window.AdvocaciaMasks) return;
		this.bindMask(frm, "cnpj", this.applyCNPJ, "cnpj");
		this.formatFormField(frm, "cnpj", this.applyCNPJ);
	},

	setupLegalCaseProcessoMask(frm) {
		const field = frm.fields_dict && frm.fields_dict.case_number;
		if (!field || !field.$input) return;

		field.$input.off(".advocacia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}

		if (frm.doc.type !== "Processo Judicial" || frm.doc.legacy_numbering) {
			return;
		}

		this.bindMask(frm, "case_number", this.applyCNJ, "cnj");

		if (frm.doc.case_number) {
			this.formatFormField(frm, "case_number", this.applyCNJ);
		}
	},
};

window.AdvocaciaMasks = AdvocaciaMasks;

window.advocacia_aplicar_mascara_input = function ($input, tipo) {
	if (!$input || !$input.length || !window.AdvocaciaMasks) return;

	const maskFns = {
		cpf: AdvocaciaMasks.applyCPF,
		cnpj: AdvocaciaMasks.applyCNPJ,
		cnj: AdvocaciaMasks.applyCNJ,
		mobile: AdvocaciaMasks.applyPhone,
		fixo: AdvocaciaMasks.applyPhone,
		phone: AdvocaciaMasks.applyPhone,
		cep: AdvocaciaMasks.applyCEP,
	};

	if ($.fn.inputmask) {
		$input.inputmask(AdvocaciaMasks._inputmaskPattern(tipo));
		return;
	}

	AdvocaciaMasks._bindInput($input, maskFns[tipo] || AdvocaciaMasks.applyPhone);
};
