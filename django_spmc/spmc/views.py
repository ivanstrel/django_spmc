from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Project, Scene


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
        project_id = request.POST["proj_id"]
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
        proj = None
        scenes = None
    else:
        proj = Project.objects.get(id=request.session.get("proj_id"))
        scenes = Scene.objects.filter(proj_id=proj).order_by("id")
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
        # Check if project id is present in request
        project_id = request.POST["proj_id"]
        if not project_id:
            return redirect("home")
        # Get selected scene id
        scene_id = request.POST["scene_id"]
        # Check that scene id is valid
        if not scene_id:
            return redirect("home")
        # Assign selected scene id to session
        request.session["scene_id"] = scene_id
        return redirect("classification")
    else:
        return redirect("home")


@login_required
def classification(request):
    context = {
        "proj_id": request.session.get("proj_id"),
        "scene_id": request.session.get("scene_id"),
    }
    return render(request, "pages/classification.html", context=context)
