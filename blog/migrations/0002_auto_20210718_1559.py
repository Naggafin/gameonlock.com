# Generated by Django 3.1.8 on 2021-07-18 19:59

from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("blog", "0001_initial"),
	]

	operations = [
		migrations.AddField(
			model_name="blogpage",
			name="author",
			field=models.CharField(default="Game on Lock", max_length=50),
		),
		migrations.AddField(
			model_name="blogpagegalleryimage",
			name="alt",
			field=models.CharField(blank=True, max_length=250),
		),
	]
