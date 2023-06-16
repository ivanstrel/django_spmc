from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from django_spmc.spmc.api.views import GetUserSuperpixels
from django_spmc.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r"users", UserViewSet)
router.register(r"superpixels", GetUserSuperpixels, basename="superpixels")


app_name = "api"
urlpatterns = router.urls
