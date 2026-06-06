"""Role definitions for Advocacia app."""
import frappe

ROLES = [
	{
		"role_name": "Advocacia User",
		"desk_access": 1,
		"is_custom": 1,
	},
	{
		"role_name": "Advocacia Manager",
		"desk_access": 1,
		"is_custom": 1,
	},
]


def create_roles():
	"""Create Advocacia roles if they don't exist."""
	for role_data in ROLES:
		if frappe.db.exists("Role", role_data["role_name"]):
			continue
		doc = frappe.new_doc("Role")
		doc.update(role_data)
		doc.insert(ignore_permissions=True)  # sistema criando roles na instalação
		frappe.logger().info(f"Role criada: {role_data['role_name']}")
