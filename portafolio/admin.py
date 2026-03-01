# portafolio/admin.py
from django.contrib import admin
from .models import Portafolio


@admin.register(Portafolio)
class PortafolioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo', 'ubicacion', 'activo', 'orden', 'created_at')
    list_filter = ('categoria', 'tipo', 'activo')
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    ordering = ('orden', '-created_at')
