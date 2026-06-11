"""Programmatic DocPerm setup for Advocacia app."""
import frappe
from frappe.permissions import setup_custom_perms
from frappe.utils import cint

ROLE_USER = "Advocacia User"
ROLE_MANAGER = "Advocacia Manager"
LEGACY_ROLES = ("Projects Manager", "Projects User")

PERM_PROPERTIES = (
	"read",
	"write",
	"create",
	"delete",
	"import",
	"export",
	"print",
	"email",
	"report",
	"share",
)

MANAGER_FULL = {
	"read": 1,
	"write": 1,
	"create": 1,
	"delete": 1,
	"import": 1,
	"export": 1,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 1,
}

USER_OPERATIONAL = {
	"read": 1,
	"write": 1,
	"create": 1,
	"delete": 0,
	"import": 0,
	"export": 0,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 0,
}

USER_READ = {
	"read": 1,
	"write": 0,
	"create": 0,
	"delete": 0,
	"import": 0,
	"export": 0,
	"print": 1,
	"email": 1,
	"report": 1,
	"share": 0,
}

MANAGER_FINANCIAL_PERMLEVEL = {
	"read": 1,
	"write": 1,
	"create": 0,
	"delete": 0,
	"import": 0,
	"export": 0,
	"print": 0,
	"email": 0,
	"report": 0,
	"share": 0,
}

USER_FINANCIAL_PERMLEVEL = {
	"read": 1,
	"write": 0,
	"create": 0,
	"delete": 0,
	"import": 0,
	"export": 0,
	"print": 0,
	"email": 0,
	"report": 0,
	"share": 0,
}

FINANCIAL = frozenset(
	{
		"Fee Agreement",
		"Legal Payment",
		"Court Cost",
		"Office Expense",
	}
)

CATALOG = frozenset(
	{
		"Jurisdiction",
		"Court Branch",
		"Court",
		"Case Phase",
		"Document Category",
		"Document Kit",
		"Document Template",
		"Office Settings",
	}
)

OPERATIONAL = frozenset(
	{
		"Legal Case",
		"Client",
		"Case Document",
		"Hearing",
		"Case Communication",
		"Deadline",
		"Service Record",
		"Time Entry",
		"Legal Task",
	}
)

MANAGED_DOCTYPES = FINANCIAL | CATALOG | OPERATIONAL

FINANCIAL_FIELD_PERMLEVEL = {
	"Fee Agreement": (
		"total_agreement_value",
		"fixed_fee_amount",
		"installment_amount",
	),
	"Legal Payment": ("amount", "received_amount"),
}


def setup_permissions():
	"""Apply Custom DocPerm rules for Advocacia User and Manager."""
	_clear_old_erpnext_roles()
	for doctype in sorted(MANAGED_DOCTYPES):
		_apply_doctype_perms(doctype)
	_apply_permlevel_fields()
	frappe.clear_cache(doctype="DocType")
	frappe.db.commit()  # setup: sincroniza permissões no migrate


def _clear_old_erpnext_roles():
	"""Remove Projects Manager/User das permissions dos DocTypes Advocacia."""
	for dt in MANAGED_DOCTYPES:
		for role in LEGACY_ROLES:
			frappe.db.delete("Custom DocPerm", {"parent": dt, "role": role})
			frappe.db.delete("DocPerm", {"parent": dt, "role": role})


def _clear_advocacia_role_perms(doctype: str, role: str):
	frappe.db.delete(
		"Custom DocPerm",
		{"parent": doctype, "role": role, "if_owner": 0},
	)


def _upsert_custom_docperm(doctype: str, role: str, permlevel: int, permissions: dict):
	setup_custom_perms(doctype)
	filters = {"parent": doctype, "role": role, "permlevel": permlevel, "if_owner": 0}
	row = {prop: cint(permissions.get(prop, 0)) for prop in PERM_PROPERTIES}
	existing = frappe.db.get_value("Custom DocPerm", filters, "name")
	if existing:
		frappe.db.set_value("Custom DocPerm", existing, row, update_modified=False)
		return

	doc = {
		"doctype": "Custom DocPerm",
		"parent": doctype,
		"parenttype": "DocType",
		"parentfield": "permissions",
		"role": role,
		"permlevel": permlevel,
		"if_owner": 0,
		**row,
	}
	frappe.get_doc(doc).insert(ignore_permissions=True)  # sistema seed de permissões


def _validate_doctype_permissions(doctype: str):
	from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype

	validate_permissions_for_doctype(doctype)


def _apply_doctype_perms(doctype: str):
	_clear_advocacia_role_perms(doctype, ROLE_MANAGER)
	_clear_advocacia_role_perms(doctype, ROLE_USER)

	if doctype in FINANCIAL:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
		_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_READ)
	elif doctype in CATALOG:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
		_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_READ)
	elif doctype in OPERATIONAL:
		_upsert_custom_docperm(doctype, ROLE_MANAGER, 0, MANAGER_FULL)
		_upsert_custom_docperm(doctype, ROLE_USER, 0, USER_OPERATIONAL)

	_validate_doctype_permissions(doctype)


def _apply_permlevel_fields():
	"""Campos financeiros com permlevel 1 — Manager write, User read."""
	for dt, fields in FINANCIAL_FIELD_PERMLEVEL.items():
		for fieldname in fields:
			if frappe.db.exists("DocField", {"parent": dt, "fieldname": fieldname}):
				frappe.db.set_value(
					"DocField",
					{"parent": dt, "fieldname": fieldname},
					"permlevel",
					1,
					update_modified=False,
				)
		_upsert_custom_docperm(dt, ROLE_MANAGER, 1, MANAGER_FINANCIAL_PERMLEVEL)
		_upsert_custom_docperm(dt, ROLE_USER, 1, USER_FINANCIAL_PERMLEVEL)
		_validate_doctype_permissions(dt)
