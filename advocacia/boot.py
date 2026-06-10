import frappe
from frappe.utils import get_url


def boot_session(bootinfo):
	"""Expõe dados do escritório no boot para print formats de relatório (client JS)."""
	office = {
		"company_name": "Escritório de Advocacia",
		"cnpj": "",
		"oab": "",
		"lawyer_name": "",
		"logo_url": "",
		"address": "",
	}

	if frappe.db.exists("DocType", "Office Settings"):
		settings = frappe.get_single("Office Settings")
		office["company_name"] = settings.company_name or office["company_name"]
		office["cnpj"] = settings.cnpj or ""
		office["oab"] = settings.oab or ""
		office["lawyer_name"] = settings.lawyer_name or ""
		office["address"] = settings.address or ""
		if settings.office_logo:
			office["logo_url"] = get_url(settings.office_logo)

	bootinfo["adv_office"] = office
