# Generated by Django 4.1.9 on 2023-06-10 17:27

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("spmc", "0002_superpixelalgo_project_srid_scene_bbox_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MiscTile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="MiscTiles name")),
                ("description", models.TextField(blank=True, verbose_name="MiscTiles description")),
                ("uuid", models.TextField(blank=True, editable=False, null=True, unique=True)),
                ("tiles_path", models.FilePathField(blank=True)),
                ("bbox", django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.RenameModel(
            old_name="ProjectAlgos",
            new_name="ProjectAlgo",
        ),
        migrations.AddField(
            model_name="scene",
            name="uuid",
            field=models.TextField(blank=True, editable=False, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="scene",
            name="bbox",
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, editable=False, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name="scene",
            name="tiles_path",
            field=models.FilePathField(blank=True, editable=False, null=True),
        ),
        migrations.DeleteModel(
            name="MiscTiles",
        ),
        migrations.AddField(
            model_name="misctile",
            name="scene_id",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="spmc.scene"),
        ),
    ]