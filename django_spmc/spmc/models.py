from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Project model for Django_SPMC
    """

    name = models.CharField(_("Project name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("Project description"), blank=True)

    def __str__(self):
        return f"Project: {self.name}"


class Scene(models.Model):
    """
    Scene model for Django_SPMC
    """

    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(_("Scene name"), max_length=255, unique=True, blank=False)
    description = models.TextField(_("Scene description"), blank=True)

    def __str__(self):
        return f"Scene: {self.name}"
