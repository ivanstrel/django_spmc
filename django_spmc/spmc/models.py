import os
import shutil
import uuid

from django.conf import settings
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


class ProjectAlgo(models.Model):
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
    uuid = models.TextField(blank=True, null=True, editable=False, unique=True)
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

    def get_center(self, srid):
        center = self.bbox.centroid
        center.transform(srid)
        return center.coords

    def gen_uuid(self):
        self.uuid = str(uuid.uuid4())


class MiscTile(models.Model):
    """
    MiscTiles model for Django_SPMC for storing paths and meta info about additional layers
    """

    scene_id = models.ForeignKey(Scene, on_delete=models.CASCADE)
    name = models.CharField(_("MiscTiles name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("MiscTiles description"), blank=True)
    uuid = models.TextField(blank=True, null=True, editable=False, unique=True)
    tiles_path = models.FilePathField(blank=True)
    bbox = models.PolygonField(blank=True, null=True, srid=4326)

    def __str__(self):
        return f"MiscTiles: {self.name}"

    def delete(self, *args, **kwargs):
        # Delete the folder associated with this object
        if os.path.exists(self.tiles_path):
            shutil.rmtree(self.tiles_path)
        super().delete(*args, **kwargs)

    def gen_uuid(self):
        self.uuid = str(uuid.uuid4())


class LandClass(models.Model):
    """
    The model to store possible land classes for Django_SPMC
    """

    name = models.CharField(_("LandClass name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("LandClass description"), blank=True)
    color = models.CharField(_("LandClass color"), max_length=255, blank=True)

    def __str__(self):
        return f"Land Class: {self.name}"


class SuperPixel(models.Model):
    """
    SuperPixel model for Django_SPMC
    """

    scene_id = models.ForeignKey(Scene, on_delete=models.CASCADE, blank=False, null=False)
    sp = models.PolygonField(blank=True, null=True, srid=4326)
    algo_id = models.ForeignKey(SuperPixelAlgo, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return f"SuperPixel: {self.id}, scene: {self.scene_id}"


class LandClassification(models.Model):
    """
    The model to store possible land classification schemas for Django_SPMC
    """

    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    land_class_id = models.ForeignKey(LandClass, on_delete=models.CASCADE)

    def __str__(self):
        return f"Land Classification. project: {self.project_id.id}, class: {self.land_class_id.name}"


class SegmentationEntry(models.Model):
    """
    Store actual classifications
    """

    scene_id = models.ForeignKey(Scene, on_delete=models.CASCADE)
    super_pixel_id = models.ForeignKey(SuperPixel, on_delete=models.CASCADE)
    land_class_id = models.ForeignKey(LandClass, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
