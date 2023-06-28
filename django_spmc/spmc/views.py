import json

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from django.shortcuts import redirect, render

from .models import LandClassification, Project, Scene


def home(request):
    if request.user.is_authenticated:
        # Authenticated users will see this template
        # Get list of all projects
        projects = Project.objects.all().values().order_by("id")
        context = {"projects": projects}
        return render(request, "pages/home_auth.html", context=context)
    else:
        # Unauthenticated users will see this template
        return render(request, "pages/home_non_auth.html")


@login_required
def select_proj(request):
    """
    View to handle selecting a project. It assigns the project_id to the request.session
    and redirect user to Scene page
    :param request:
    :return:
    """
    if request.method == "POST":
        project_id = request.POST.get("proj_id")
        # Check if project id is valid
        if not Project.objects.filter(id=project_id).exists():
            return redirect("home")
        request.session["proj_id"] = project_id
        # We have to drop any previously selected Scenes as we are selecting a new project
        request.session["scene_id"] = None
        return redirect("scene")
    else:
        return redirect("home")


@login_required
def scene(request):
    # Check if proj_id is in session data
    if not request.session.get("proj_id"):
        return redirect("home")
    else:
        proj = Project.objects.get(id=request.session.get("proj_id"))
        # Select scenes and corresponding unique algo_ids (i.e unique pairs of scene_id and related superpixel.algo_id)
        scenes = (
            Scene.objects.filter(superpixel__scene_id__proj_id=proj)
            .annotate(
                algo_id=F("superpixel__algo_id"),
                algo_name=F("superpixel__algo_id__name"),
                algo_descr=F("superpixel__algo_id__description"),
            )
            .distinct()
        )
    context = {
        "proj": proj,
        "scenes": scenes,
    }
    return render(request, "pages/scene.html", context=context)


@login_required
def select_scene(request):
    """
    View to handle selecting a scene. It assigns the scene_id to the request.session and redirect user to
    Classification page
    :param request:
    :return:
    """
    if request.method == "POST":
        # Check if project, scene and algo id is present in request
        project_id = request.POST.get("proj_id")
        scene_id = request.POST.get("scene_id")
        algo_id = request.POST.get("algo_id")
        if not project_id or not scene_id or not algo_id:
            return redirect("home")

        # Assign selected scene and algo id to session
        request.session["scene_id"] = scene_id
        request.session["algo_id"] = algo_id
        return redirect("classification")
    else:
        return redirect("home")


@login_required
def classification(request):
    project_id = request.session.get("proj_id")
    scene_id = request.session.get("scene_id")
    algo_id = request.session.get("algo_id")
    # Check if proj_id is in session data
    if not project_id:
        return redirect("home")
    # Check if scene and algo id is in session data
    if not scene_id or not algo_id:
        return redirect("scene")
    # Prepare context ========================================================
    scene_obj = Scene.objects.get(id=scene_id)
    proj_obj = Project.objects.get(id=project_id)
    # Prepare classes and colors dict
    class_col = (
        LandClassification.objects.filter(project_id=proj_obj)
        .annotate(color=F("land_class_id__color"))
        .annotate(name=F("land_class_id__name"))
        .order_by("id")
        .annotate(key=Window(expression=RowNumber()))
    )
    class_col_json = json.dumps(list(class_col.values()), cls=DjangoJSONEncoder)
    # misc_tiles = MiscTile.objects.filter(scene_id=scene_obj)
    context = {
        "proj_id": project_id,
        "scene_id": scene_id,
        "algo_id": algo_id,
        "scene": scene_obj,
        "map_center": scene_obj.get_center(3857),
        "user_id": request.user.pk,
        "class_col": class_col,
        "class_col_json": class_col_json,
    }
    return render(request, "pages/classification.html", context=context)
