frappe.ui.form.on('Cliente', {
    refresh: function(frm) {
        aplicar_mascaras_cliente(frm);
    },
    tipo_pessoa: function(frm) {
        aplicar_mascaras_cliente(frm);
    }
});

frappe.ui.form.on('Contato Cliente', {
    form_render: function(frm) {
        aplicar_mascaras_contato_row(frm);
    }
});

function aplicar_mascaras_cliente(frm) {
    if (frm.doc.tipo_pessoa === 'Pessoa Física') {
        advocacia_aplicar_mascara(frm, 'cpf', 'cpf');
        advocacia_limpar_mascara(frm, 'cnpj');
    } else if (frm.doc.tipo_pessoa === 'Pessoa Jurídica') {
        advocacia_aplicar_mascara(frm, 'cnpj', 'cnpj');
        advocacia_limpar_mascara(frm, 'cpf');
        advocacia_aplicar_mascara(frm, 'cpf_representante', 'cpf');
    }
}

function aplicar_mascaras_contato_row(frm) {
    ['telefone', 'celular'].forEach(function(fieldname) {
        var field = frm.fields_dict[fieldname];
        if (!field || !field.$input) return;
        var tipo = fieldname === 'celular' ? 'celular' : 'fixo';
        advocacia_aplicar_mascara_input(field.$input, tipo);
    });
}

function advocacia_limpar_mascara(frm, fieldname) {
    var field = frm.fields_dict[fieldname];
    if (field && field.$input) {
        field.$input.off('.advocacia_mask');
        if ($.fn.inputmask && field.$input.inputmask) {
            field.$input.inputmask('remove');
        }
    }
}

function advocacia_aplicar_mascara(frm, fieldname, tipo) {
    var field = frm.fields_dict[fieldname];
    if (!field || !field.$input) return;
    advocacia_aplicar_mascara_input(field.$input, tipo);
}

function advocacia_aplicar_mascara_input($input, tipo) {
    if (!$input || !$input.length) return;

    var patterns = {
        cpf: '999.999.999-99',
        cnpj: '99.999.999/9999-99',
        cnj: '9999999-99.9999.9.99.9999',
        celular: '(99) 99999-9999',
        fixo: '(99) 9999-9999'
    };

    if ($.fn.inputmask) {
        $input.inputmask(patterns[tipo] || '');
        return;
    }

    $input.off('input.advocacia_mask').on('input.advocacia_mask', function() {
        var digits = $input.val().replace(/\D/g, '');
        $input.val(advocacia_formatar_mascara(tipo, digits));
    });
}

function advocacia_formatar_mascara(tipo, digits) {
    if (!digits) return '';

    if (tipo === 'cpf') {
        digits = digits.slice(0, 11);
        return digits
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    }
    if (tipo === 'cnpj') {
        digits = digits.slice(0, 14);
        return digits
            .replace(/^(\d{2})(\d)/, '$1.$2')
            .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
            .replace(/\.(\d{3})(\d)/, '.$1/$2')
            .replace(/(\d{4})(\d)/, '$1-$2');
    }
    if (tipo === 'cnj') {
        digits = digits.slice(0, 20);
        return digits
            .replace(/^(\d{7})(\d)/, '$1-$2')
            .replace(/^(\d{7})-(\d{2})(\d)/, '$1-$2.$3')
            .replace(/\.(\d{4})(\d)/, '.$1.$2')
            .replace(/\.(\d{4})\.(\d)(\d{2})/, '.$1.$2.$3')
            .replace(/\.(\d{4})\.(\d)\.(\d{2})(\d)/, '.$1.$2.$3.$4');
    }
    if (tipo === 'celular') {
        digits = digits.slice(0, 11);
        if (digits.length <= 2) return digits.length ? '(' + digits : '';
        if (digits.length <= 7) return '(' + digits.slice(0, 2) + ') ' + digits.slice(2);
        return '(' + digits.slice(0, 2) + ') ' + digits.slice(2, 7) + '-' + digits.slice(7);
    }
    if (tipo === 'fixo') {
        digits = digits.slice(0, 10);
        if (digits.length <= 2) return digits.length ? '(' + digits : '';
        if (digits.length <= 6) return '(' + digits.slice(0, 2) + ') ' + digits.slice(2);
        return '(' + digits.slice(0, 2) + ') ' + digits.slice(2, 6) + '-' + digits.slice(6);
    }
    return digits;
}
