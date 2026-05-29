frappe.ui.form.on('Servico', {
    refresh: function(frm) {
        if (frm.fields_dict.numero_processo) {
            var $cnj = frm.fields_dict.numero_processo.$input;
            if ($cnj && $cnj.length) {
                if ($.fn.inputmask) {
                    $cnj.inputmask('9999999-99.9999.9.99.9999');
                } else {
                    $cnj.off('input.advocacia_cnj').on('input.advocacia_cnj', function() {
                        var digits = $cnj.val().replace(/\D/g, '').slice(0, 20);
                        $cnj.val(digits
                            .replace(/^(\d{7})(\d)/, '$1-$2')
                            .replace(/^(\d{7})-(\d{2})(\d)/, '$1-$2.$3')
                            .replace(/\.(\d{4})(\d)/, '.$1.$2')
                            .replace(/\.(\d{4})\.(\d)(\d{2})/, '.$1.$2.$3')
                            .replace(/\.(\d{4})\.(\d)\.(\d{2})(\d)/, '.$1.$2.$3.$4'));
                    });
                }
            }
        }
        if (!frm.is_new()) {
            frm.add_custom_button(__('Gerar Documento'), function() {
                frappe.call({
                    method: 'advocacia.advocacia.documentos.get_templates_disponiveis',
                    callback: function(r) {
                        if (!r.message || r.message.length === 0) {
                            frappe.msgprint(__('Nenhum template cadastrado. Va em Template Documento para cadastrar.'));
                            return;
                        }
                        var options = r.message.map(function(t) { return t.name; }).join('\n');
                        var d = new frappe.ui.Dialog({
                            title: __('Selecionar Template'),
                            fields: [
                                {
                                    fieldname: 'template',
                                    fieldtype: 'Link',
                                    label: __('Template'),
                                    options: 'Template Documento',
                                    reqd: 1,
                                    get_query: function() {
                                        return { filters: { habilitado: 1 } };
                                    }
                                }
                            ],
                            primary_action_label: __('Gerar'),
                            primary_action: function(values) {
                                d.hide();
                                frappe.call({
                                    method: 'advocacia.advocacia.documentos.gerar_documento',
                                    args: {
                                        servico_name: frm.doc.name,
                                        template_name: values.template
                                    },
                                    freeze: true,
                                    freeze_message: __('Gerando documento...'),
                                    callback: function(r) {
                                        if (r.message) {
                                            frappe.msgprint({
                                                title: __('Documento Gerado'),
                                                message: __('Arquivo: ') + r.message.file_name +
                                                    '<br><br><a href="' + r.message.file_url +
                                                    '" target="_blank" class="btn btn-primary btn-sm">' +
                                                    __('Baixar Documento') + '</a>',
                                                indicator: 'green'
                                            });
                                            frm.reload_doc();
                                        }
                                    }
                                });
                            }
                        });
                        d.show();
                    }
                });
            }, __('Documentos'));
        }
    }
});
