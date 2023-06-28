from django.contrib.gis.db.models.functions import AsGeoJSON, Transform
from django.db.models import OuterRef, Subquery
from rest_framework import authentication, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_spmc.spmc.models import LandClass, LandClassification, Scene, SegmentationEntry, SuperPixel


class GetUserSuperpixels(viewsets.ViewSet):
    authentication_classes = [authentication.SessionAuthentication]

    @action(detail=False, methods=["post"])
    def get_sp(self, request):
        # TODO replace most of this with session data, as we store project, scene and algo in session
        srid = self.request.data.get("srid")
        user_id = self.request.user.id
        scene_id = self.request.data.get("scene_id")
        algo_id = self.request.data.get("algo_id")
        proj_id = Scene.objects.get(id=scene_id).proj_id

        # Get all Superpixels for given scene
        entries = SegmentationEntry.objects.filter(
            super_pixel_id=OuterRef("pk"), scene_id__id=scene_id, user_id__id=user_id
        )
        colors = LandClass.objects.filter(
            id__in=LandClassification.objects.filter(project_id=proj_id).values_list("land_class_id")
        ).filter(id=OuterRef("land_class_id"))
        sp = (
            SuperPixel.objects.filter(scene_id__id=scene_id, algo_id__id=algo_id)
            .annotate(land_class_id=Subquery(entries.values("land_class_id")))
            .annotate(entry_id=Subquery(entries.values("id")))
            .annotate(color=Subquery(colors.values("color")))
            # Here is a fastest version of geojson serialization (need processing on js side)
            .annotate(features=AsGeoJSON(Transform("sp", srid)))
        ).values("id", "land_class_id", "color", "features")
        return Response(sp)

    @action(detail=False, methods=["post"], name="save-sp")
    def save_sp(self, request):
        upd_list = request.data.get("upd")
        for entry in upd_list:
            user_id = request.user.id
            scene_id = entry.get("scene_id")
            sp_id = entry.get("superpixel_id")
            land_class_id = entry.get("class_id")

            # Check if such entry is already in database
            obj = SegmentationEntry.objects.filter(
                scene_id__id=scene_id, super_pixel_id__id=sp_id, user_id__id=user_id
            )
            if obj.exists():
                # This is an update case
                obj = obj.get()
                obj.land_class_id = LandClass(id=land_class_id)
                obj.save()
            else:
                # This is a creation case
                SegmentationEntry(
                    user_id=request.user,
                    super_pixel_id=SuperPixel.objects.get(id=sp_id),
                    scene_id=Scene.objects.get(id=scene_id),
                    land_class_id=LandClass.objects.get(id=land_class_id),
                ).save()

        return Response({"code": "done"})
