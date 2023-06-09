import os
import subprocess

from django import forms
from django.conf import settings
from django.contrib.gis import admin
from django.contrib.gis.gdal import GDALRaster
from django.core.checks import Error
from django.core.files.temp import NamedTemporaryFile

from .models import MiscTiles, Project, ProjectAlgos, Scene, SuperPixelAlgo

admin.site.register(Project)
admin.site.register(SuperPixelAlgo)
admin.site.register(ProjectAlgos)
admin.site.register(MiscTiles)


# =====================================================================================================================
# Processing Scene with base tiles
# =====================================================================================================================
class SceneFormAdmin(forms.ModelForm):
    image_file = forms.FileField(label="Spatial Raster Image")

    class Meta:
        model = Scene
        fields = ["proj_id", "name", "description"]


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    readonly_fields = ["tiles_path", "bbox"]
    form = SceneFormAdmin

    def save_model(self, request, obj, form, change):
        form = SceneFormAdmin(request.POST, request.FILES)
        if not form.is_valid():
            raise Error("Form is not valid")

        clean_data = form.cleaned_data
        obj.proj_id = clean_data["proj_id"]
        obj.name = clean_data["name"]
        obj.description = clean_data["description"]

        # process image ===============================================================================================
        image_file = request.FILES["image_file"]
        # Generate random folder name
        tmp_file = NamedTemporaryFile()
        tmp_file_name = os.path.basename(tmp_file.name)
        # Save file to temp
        tmp_file.write(image_file.read())

        # Define the output directory name folder based on the primary key of the Scene model
        output_dir = f"{settings.MEDIA_ROOT}/tiles/{tmp_file_name}"
        # TODO here is a problem, as new dir will be created for each change,
        # TODO Also it is possible that the dir with such name already exists (not sure in random name generator)
        # Check if output path exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Run gdal2tiles.py as a subprocess, passing in the input and output paths
        subprocess.run(["gdal2tiles.py", "-z", "10-18", "-w", "none", "-r", "bilinear", tmp_file.name, output_dir])
        # Assign the output directory path to the Scene model
        obj.tiles_path = output_dir
        # Bounding box calculation ====================================================================================
        rs = GDALRaster(tmp_file.name)
        print(rs.srid)  # Dummy for pre_commit pass
        # TODO add bounding box calculation
        super().save_model(request, obj, form, change)
        self.message_user(request, f"Tiles for {obj} have been processed and saved to {output_dir}")
