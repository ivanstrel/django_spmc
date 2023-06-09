# Generated by Django 4.1.9 on 2023-05-28 00:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="Project name")),
                ("description", models.TextField(blank=True, verbose_name="Project description")),
            ],
        ),
        migrations.CreateModel(
            name="Scene",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="Scene name")),
                ("description", models.TextField(blank=True, verbose_name="Scene description")),
                ("proj_id", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="spmc.project")),
            ],
        ),
    ]
