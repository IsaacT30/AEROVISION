# portafolio/urls.py
from rest_framework.routers import DefaultRouter
from .views import PortafolioViewSet

router = DefaultRouter()
router.register(r'portafolio', PortafolioViewSet, basename='portafolio')

urlpatterns = router.urls
