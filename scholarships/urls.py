from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet, DashboardView, ProgramViewSet

router = DefaultRouter()
router.register("programs", ProgramViewSet)
router.register("applications", ApplicationViewSet, basename="application")
urlpatterns = [path("", include(router.urls)), path("dashboard/", DashboardView.as_view())]
