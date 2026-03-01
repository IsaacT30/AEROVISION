"""
URL configuration for aerovision_api project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('users.urls')),        # Auth & Users
    path('api/', include('services.urls')),     # Services (drones)
    path('api/', include('bookings.urls')),     # Bookings (reservas)
    path('api/', include('portafolio.urls')),   # Portafolio
    path('api/', include('leads.urls')),        # Leads (consultas)
]
