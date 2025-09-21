# home/migrations/0002_create_default_homepage.py
from django.db import migrations


def create_default_homepage(apps, schema_editor):
	HomePage = apps.get_model("gameonlock", "HomePage")
	Page = apps.get_model("wagtailcore", "Page")

	# Check if a HomePage already exists
	if HomePage.objects.exists():
		return

	# Get the root page (default site)
	root_page = Page.objects.get(id=1)  # Usually root page has ID=1
	homepage = HomePage()
	root_page.add_child(instance=homepage)
	homepage.save_revision().publish()


class Migration(migrations.Migration):
	dependencies = [
		("gameonlock", "0001_initial"),
	]

	operations = [
		migrations.RunPython(create_default_homepage),
	]
