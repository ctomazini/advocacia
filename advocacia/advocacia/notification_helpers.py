import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification


def notification_already_sent(document_type, document_name, subject):
	return frappe.db.exists(
		"Notification Log",
		{
			"document_type": document_type,
			"document_name": document_name,
			"subject": subject,
		},
	)


def send_system_notification(users, doctype, docname, subject, message):
	users = [u for u in users if u]
	if not users:
		users = ["Administrator"]
	enqueue_create_notification(
		users=users,
		doc={
			"type": "Alert",
			"document_type": doctype,
			"document_name": docname,
			"subject": subject,
			"email_content": message,
			"from_user": frappe.session.user or "Administrator",
		},
	)
