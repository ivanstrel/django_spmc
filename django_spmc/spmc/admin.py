import json

from django import forms
from django.contrib.gis import admin
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.exceptions import RequestAborted, ValidationError
from django.core.validators import FileExtensionValidator

from .models import (
    LandClass,
    LandClassification,
    MiscTile,
    Project,
    ProjectAlgo,
    Scene,
    SegmentationEntry,
    SuperPixel,
    SuperPixelAlgo,
)
from .utils import check_geojson, check_raster, handle_tiles_upload

admin.site.register(Project)
admin.site.register(SuperPixelAlgo)
admin.site.register(ProjectAlgo)
admin.site.register(SuperPixel)
admin.site.register(LandClassification)
admin.site.register(SegmentationEntry)


# =====================================================================================================================
# Land class
# =====================================================================================================================
class LandClassFormAdmin(forms.ModelForm):
    color = forms.CharField(label="Class color", max_length=7, widget=forms.TextInput(attrs={"type": "color"}))


@admin.register(LandClass)
class LandClassAdmin(admin.ModelAdmin):
    fields = ["name", "description", "color"]
    form = LandClassFormAdmin


# =====================================================================================================================
# Processing Scene with base tiles
# =====================================================================================================================
class MiscTileInline(admin.TabularInline):
    model = MiscTile
    fields = ["name", "description", "uuid", "tiles_path", "bbox"]
    readonly_fields = ["uuid", "tiles_path", "bbox"]


class SceneFormAdmin(forms.ModelForm):
    json_file = forms.FileField(
        label="GeoJSON with superpixel polygons",
        required=False,
        validators=[FileExtensionValidator(["json", "geojson"])],
    )
    algo_id = forms.ModelChoiceField(queryset=SuperPixelAlgo.objects.all(), required=False)
    image_file = forms.FileField(label="Spatial Raster Image", required=False)

    def clean(self):
        cleaned_data = super().clean()
        # Check raster
        im_file = cleaned_data["image_file"]
        # Check if it could be processed with gdal2tiles
        if "image_file" in self.changed_data:
            check_raster(im_file)
        # Check json if needed
        if not cleaned_data.get("json_file") is None:
            json_file = cleaned_data["json_file"]
            scene = self.instance
            scene_bbox = None
            if scene.bbox is not None:
                scene_bbox = scene.bbox
            check_geojson(json_file, scene_bbox, im_file)
        return cleaned_data

    def clean_algo_id(self):
        algo_id = self.cleaned_data["algo_id"]
        if self.instance.pk is None:  # Check if it is a new Scene object
            if algo_id is None:
                raise ValidationError("To create a new entry, please specify an algorythm")
        # Algo id should be present if new SuperPixels provided
        if "json_file" in self.changed_data:
            if algo_id is None:
                raise ValidationError("Please specify an algorythm")
        return self.cleaned_data["algo_id"]

    def clean_image_file(self):
        # We want the user to provide image file on Scene creation. On the Scene change, the field is optional
        im_file = self.cleaned_data["image_file"]
        if self.instance.pk is None:  # Check if it is a new Scene object
            if im_file is None:
                raise ValidationError("To create a new entry, please provide the raster file")
        return self.cleaned_data["image_file"]

    def clean_json_file(self):
        # We need to check that the file is geojson, polygon, and could be read with GEOSGeometry
        im_file = self.cleaned_data["json_file"]
        if self.instance.pk is None:  # Check if it is a new Scene object
            if im_file is None:
                raise ValidationError("To create a new entry, please provide the json file")
        return self.cleaned_data["json_file"]

    class Meta:
        model = Scene
        fields = []


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    fields = ["proj_id", "name", "description", "image_file", "json_file", "algo_id", "uuid", "tiles_path", "bbox"]
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
                # Can not figure out how to handle this (form.add_error does not prevent for model saving)
                raise RequestAborted(err)

            obj.tiles_path = output_dir
            # Add bounding box to model obj, control for srid
            poly = Polygon.from_bbox(bbox)
            poly.srid = srid
            # Reproject bbox polygon to Scene model srid
            poly.transform(Scene.bbox.field.srid)
            obj.bbox = poly
            self.message_user(request, f"Tiles for {obj} have been processed and saved to {output_dir}")

        # Check if Superpixel Geojoson need to be processed
        if (not form.cleaned_data["json_file"] is None) and ("json_file" in form.changed_data):
            # First check if our object has pk (or it is new, if so save current)
            if obj.pk is None:
                obj.save()
                change = True  # So the super().save_model will treat subsequent additions as changes
            else:  # The case of update (delete existent polys only if algo_id is the same)
                SuperPixel.objects.filter(scene_id=obj).filter(algo_id=form.cleaned_data.get("algo_id")).delete()

            # Read geojson file (do not know why, but I was able to read it only via chunks)
            json_str = ""
            for chunk in request.FILES["json_file"].chunks():
                json_str += chunk.decode("utf-8")
            geojson_data = json.loads(json_str)

            # Loop over features and save them
            for feature in geojson_data.get("features", []):
                feature_str = feature.get("geometry")
                feature_str.update({"crs": geojson_data.get("crs")})
                tmp_geom = GEOSGeometry(json.dumps(feature_str))
                tmp_geom.transform(obj.bbox.srid)
                # Save to SuperPixel model
                new_sp_obj = SuperPixel(scene_id=obj, algo_id=form.cleaned_data["algo_id"], sp=tmp_geom)
                new_sp_obj.save()
        # Call super save
        super().save_model(request, obj, form, change)


# =====================================================================================================================
# Processing MiscTile model
# =====================================================================================================================
class MiscTileFormAdmin(SceneFormAdmin):
    def clean_json_file(self):
        return None

    def clean_algo_id(self):
        return None

    class Meta:
        model = MiscTile
        fields = []


@admin.register(MiscTile)
class MiscTileAdmin(SceneAdmin):
    fields = ["scene_id", "name", "description", "image_file", "uuid", "tiles_path", "bbox"]
    readonly_fields = ["uuid", "tiles_path", "bbox"]
    exclude = ["json_file", "algo_id"]
    inlines = []
    form = MiscTileFormAdmin
