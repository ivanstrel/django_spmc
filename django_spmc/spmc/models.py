import os
import shutil

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Project model for Django_SPMC
    """

    name = models.CharField(_("Project name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("Project description"), blank=True)
    srid = models.IntegerField(default=3857)  # Default Spatial Reference ID of a project

    def __str__(self):
        return f"Project: {self.name}"


class SuperPixelAlgo(models.Model):
    """
    SuperPixelType model for Django_SPMC
    """

    name = models.CharField(_("SuperPixelType name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("SuperPixelType description"), blank=True)

    def __str__(self):
        return f"SP algorithm: {self.name}"


class ProjectAlgos(models.Model):
    """
    List of approved Superpixel algorithms for each project
    """

    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    algo_id = models.ForeignKey(SuperPixelAlgo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Proj-Algo pair: {self.proj_id} - {self.algo_id}"


class Scene(models.Model):
    """
    Scene model for Django_SPMC
    """

    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(_("Scene name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("Scene description"), blank=True, null=True)
    tiles_path = models.FilePathField(blank=True, null=True, editable=False)
    bbox = models.PolygonField(blank=True, null=True, srid=4326, editable=False)

    def __str__(self):
        return f"Scene: {self.name}"

    def delete(self, *args, **kwargs):
        # Delete the folder associated with this object
        if self.tiles_path:
            if os.path.exists(self.tiles_path):
                shutil.rmtree(self.tiles_path)
        super().delete(*args, **kwargs)


class MiscTiles(models.Model):
    """
    MiscTiles model for Django_SPMC for storing paths and meta info about additional layers
    """

    scene_id = models.ForeignKey(Scene, on_delete=models.CASCADE)
    name = models.CharField(_("MiscTiles name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("MiscTiles description"), blank=True)
    tiles_path = models.FilePathField(blank=True)
    bbox = models.PolygonField(blank=True, null=True, srid=4326)

    def __str__(self):
        return f"MiscTiles: {self.name}"

    def delete(self, *args, **kwargs):
        # Delete the folder associated with this object
        if os.path.exists(self.tiles_path):
            shutil.rmtree(self.tiles_path)
        super().delete(*args, **kwargs)


class SuperPixel(models.Model):
    """
    SuperPixel model for Django_SPMC
    """

    scene_id = models.ForeignKey(Scene, on_delete=models.CASCADE)
    sp = models.PolygonField(blank=True, null=True, srid=4326)
    algo_id = models.ForeignKey(SuperPixelAlgo, on_delete=models.CASCADE)

    def __str__(self):
        return f"SuperPixel: {self.id}, scene: {self.scene_id}"
