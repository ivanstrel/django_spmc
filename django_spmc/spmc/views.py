from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    if request.user.is_authenticated:
        # Authenticated users will see this template
        return render(request, "pages/home_auth.html")
    else:
        # Unauthenticated users will see this template
        return render(request, "pages/home_non_auth.html")


@login_required
def scene(request):
    context = {
        "proj_id": request.session.get("proj_id"),
    }
    return render(request, "pages/scene.html", context=context)


@login_required
def classification(request):
    context = {
        "proj_id": request.session.get("proj_id"),
        "scene_id": request.session.get("scene_id"),
    }
    return render(request, "pages/classification.html", context=context)
