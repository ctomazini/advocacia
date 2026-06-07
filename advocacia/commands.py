"""Custom bench commands for Advocacia app."""

import click
import frappe
from frappe.commands import get_site, pass_context


@click.command("seed-demo-advocacia")
@click.option("--site", help="Site name")
@pass_context
def seed_demo_advocacia(context, site=None):
	"""Populate site with Advocacia demo data for testing."""
	site = site or get_site(context)
	frappe.init(site=site)
	frappe.connect()
	try:
		from advocacia.advocacia.setup.seed_demo import seed_demo_data

		count = seed_demo_data()
		click.echo(f"✅ {count} documentos demo criados em {site}")
	finally:
		frappe.destroy()


@click.command("clear-demo-advocacia")
@click.option("--site", help="Site name")
@pass_context
def clear_demo_advocacia(context, site=None):
	"""Remove all Advocacia demo data from site."""
	site = site or get_site(context)
	frappe.init(site=site)
	frappe.connect()
	try:
		from advocacia.advocacia.setup.seed_demo import clear_demo_data

		count = clear_demo_data()
		click.echo(f"🗑️  {count} documentos demo removidos de {site}")
	finally:
		frappe.destroy()


# Aliases — podem ser sobrescritos se outro app registrar seed-demo
@click.command("seed-demo")
@click.option("--site", help="Site name")
@pass_context
def seed_demo(context, site=None):
	seed_demo_advocacia.callback(context, site=site)


@click.command("clear-demo")
@click.option("--site", help="Site name")
@pass_context
def clear_demo(context, site=None):
	clear_demo_advocacia.callback(context, site=site)


commands = [seed_demo_advocacia, clear_demo_advocacia, seed_demo, clear_demo]
