from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def is_account_section_active(context):
	request = context.get("request")

	if not request:
		return False

	current_path = request.path

	account_paths = [
		reverse("dashboard"),
		reverse("play_history"),
		reverse("transaction_history"),
		reverse("settings"),
	]

	return current_path in account_paths
