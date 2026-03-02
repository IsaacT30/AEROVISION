# bookings/urls.py
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'reservas', BookingViewSet, basename='booking')

urlpatterns = router.urls
