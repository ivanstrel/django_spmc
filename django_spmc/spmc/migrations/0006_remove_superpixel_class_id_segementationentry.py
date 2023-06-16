# Generated by Django 4.1.9 on 2023-06-16 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("spmc", "0005_remove_landclassification_description_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="superpixel",
            name="class_id",
        ),
        migrations.CreateModel(
            name="SegementationEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("land_class_id", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="spmc.landclass")),
                ("scene_id", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="spmc.scene")),
                (
                    "super_pixel_id",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="spmc.superpixel"),
                ),
                (
                    "user_id",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
