import json
import os

import frappe


def _workspace_json_path():
	return frappe.get_app_path(
		"advocacia",
		"advocacia",
		"workspace",
		"advocacia",
		"advocacia.json",
	)


def _fixture_workspace_path():
	return frappe.get_app_path("advocacia", "fixtures", "workspace.json")


def _ensure_workspace_json_on_disk():
	"""Garante JSON canônico no path esperado pelo sync (evita orphan cleanup)."""
	path = _workspace_json_path()
	if os.path.exists(path):
		return path

	fixture_path = _fixture_workspace_path()
	if not os.path.exists(fixture_path):
		frappe.logger().warning("Workspace fixture não encontrado: %s", fixture_path)
		return None

	with open(fixture_path) as f:
		data = json.load(f)
	doc = data[0] if isinstance(data, list) else data
	doc["module"] = "Advocacia"
	doc["app"] = "advocacia"
	doc["public"] = 1
	doc["name"] = "Advocacia"
	doc["label"] = "Advocacia"

	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w") as f:
		json.dump(doc, f, indent=1, ensure_ascii=False)
		f.write("\n")

	return path


def ensure_advocacia_workspace():
	"""Sincroniza o Workspace Advocacia a partir do JSON do módulo (idempotente)."""
	path = _ensure_workspace_json_on_disk()
	if not path:
		return

	frappe.import_doc(path)

	if frappe.db.exists("Workspace", "Advocacia"):
		frappe.db.set_value(
			"Workspace",
			"Advocacia",
			{"module": "Advocacia", "app": "advocacia", "public": 1},
			update_modified=False,
		)

	frappe.clear_cache()
	frappe.db.commit()
