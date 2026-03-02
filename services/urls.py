# services/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet
from .upload_views import upload_file

router = DefaultRouter()
router.register(r'servicios', ServiceViewSet, basename='service')

urlpatterns = [
    path('upload/', upload_file, name='upload'),
] + router.urls
