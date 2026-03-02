"""
URL configuration for aerovision_api project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('users.urls')),        # Auth & Users
    path('api/', include('services.urls')),     # Services (drones)
    path('api/', include('bookings.urls')),     # Bookings (reservas)
    path('api/', include('portafolio.urls')),   # Portafolio
    path('api/', include('leads.urls')),        # Leads (consultas)
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
