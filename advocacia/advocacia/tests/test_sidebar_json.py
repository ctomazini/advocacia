import json
import os
import unittest

from advocacia.advocacia.setup.sidebar import SIDEBAR_LINK_ORDER, SIDEBAR_SECTIONS


def _sidebar_json_path():
	return os.path.join(
		os.path.dirname(__file__),
		"..",
		"..",
		"workspace_sidebar",
		"advocacia.json",
	)


def _app_package_root():
	return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestSidebarJson(unittest.TestCase):
	def test_workspace_sidebar_matches_canonical_order(self):
		with open(_sidebar_json_path(), encoding="utf-8") as handle:
			doc = json.load(handle)

		links = [
			(item["label"], item.get("link_to"), item["link_type"])
			for item in doc["items"]
			if item.get("type") == "Link"
		]
		expected = list(SIDEBAR_LINK_ORDER)

		self.assertEqual(
			len(links),
			len(expected),
			f"sidebar JSON has {len(links)} links; SIDEBAR_LINK_ORDER has {len(expected)}",
		)
		for idx, (actual, want) in enumerate(zip(links, expected, strict=True)):
			self.assertEqual(
				actual,
				want,
				f"link #{idx + 1}: expected {want}, got {actual}",
			)

	def test_workspace_sidebar_sections_match(self):
		with open(_sidebar_json_path(), encoding="utf-8") as handle:
			doc = json.load(handle)

		sections = [
			{
				"label": item["label"],
				"collapsible": item.get("collapsible"),
				"keep_closed": item.get("keep_closed"),
			}
			for item in doc["items"]
			if item.get("type") == "Section Break"
		]

		self.assertEqual(len(sections), len(SIDEBAR_SECTIONS))
		for idx, (actual, want) in enumerate(zip(sections, SIDEBAR_SECTIONS, strict=True)):
			self.assertEqual(actual, want, f"section #{idx + 1}: expected {want}, got {actual}")

	def test_sidebar_link_targets_exist_in_app(self):
		app_root = _app_package_root()
		for label, link_to, link_type in SIDEBAR_LINK_ORDER:
			if link_type == "DocType":
				slug = link_to.lower().replace(" ", "_")
				path = os.path.join(app_root, "doctype", slug)
				self.assertTrue(os.path.isdir(path), f"{label}: DocType folder missing: {path}")
			elif link_type == "Report":
				path = os.path.join(app_root, "report", link_to)
				self.assertTrue(os.path.isdir(path), f"{label}: Report folder missing: {path}")
			elif link_type == "Page":
				path = os.path.join(app_root, "page", link_to)
				self.assertTrue(os.path.isdir(path), f"{label}: Page folder missing: {path}")
			else:
				self.fail(f"{label}: unsupported link_type {link_type}")
