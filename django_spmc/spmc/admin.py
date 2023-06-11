from django import forms
from django.contrib.gis import admin
from django.contrib.gis.geos import Polygon
from django.core.exceptions import RequestAborted, ValidationError

from .models import MiscTile, Project, ProjectAlgo, Scene, SuperPixelAlgo
from .utils import handle_tiles_upload

admin.site.register(Project)
admin.site.register(SuperPixelAlgo)
admin.site.register(ProjectAlgo)


# =====================================================================================================================
# Processing Scene with base tiles
# =====================================================================================================================
class MiscTileInline(admin.TabularInline):
    model = MiscTile
    fields = ["name", "description", "uuid", "tiles_path", "bbox"]
    readonly_fields = ["uuid", "tiles_path", "bbox"]


class SceneFormAdmin(forms.ModelForm):
    image_file = forms.FileField(label="Spatial Raster Image", required=False)

    def clean_image_file(self):
        # We want the user to provide image file on Scene creation. On the Scene change, the field is optional
        im_file = self.cleaned_data["image_file"]
        if self.instance.pk is None:  # Check if it is a new Scene object
            if im_file is None:
                raise ValidationError("To create a new entry, please provide the raster file")

    class Meta:
        model = Scene
        fields = []


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    fields = ["proj_id", "name", "description", "image_file", "uuid", "tiles_path", "bbox"]
    readonly_fields = ["uuid", "tiles_path", "bbox"]
    inlines = [MiscTileInline]
    form = SceneFormAdmin

    def save_model(self, request, obj, form, change):
        if not form.is_valid():
            # If something wrong, just let super method to handle that
            super().save_model(request, obj, form, change)

        # process image ===============================================================================================
        # Here we want to process image only if it is in changed form data (pass if a new file was not provided)
        if "image_file" in form.changed_data:
            # Generate uuid field if not present
            if obj.uuid is None:
                obj.gen_uuid()
                scene_uuid = obj.uuid
            else:
                scene_uuid = obj.uuid
            # Process image
            output_dir, bbox, srid, err = handle_tiles_upload(request.FILES["image_file"], scene_uuid)
            # Check output for errors
            if err is not None:
                # TODO can not figure out how to handle this (form.add_error does not prevent for saving)
                raise RequestAborted(err)

            obj.tiles_path = output_dir
            # Add bounding box to model obj, control for srid
            poly = Polygon.from_bbox(bbox)
            poly.srid = srid
            # Reproject bbox polygon to Scene model srid
            poly.transform(Scene.bbox.field.srid)
            obj.bbox = poly
            self.message_user(request, f"Tiles for {obj} have been processed and saved to {output_dir}")
        # Call super save
        super().save_model(request, obj, form, change)


# =====================================================================================================================
# Processing MiscTile model
# =====================================================================================================================
class MiscTileFormAdmin(SceneFormAdmin):
    class Meta:
        model = MiscTile
        fields = []


@admin.register(MiscTile)
class MiscTileAdmin(SceneAdmin):
    fields = ["scene_id", "name", "description", "image_file", "uuid", "tiles_path", "bbox"]
    readonly_fields = ["uuid", "tiles_path", "bbox"]
    inlines = []
    form = MiscTileFormAdmin
