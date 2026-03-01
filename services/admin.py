# services/admin.py
from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_base', 'precio_por_hora', 'horas_minimas', 'activo', 'orden')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    ordering = ('orden', 'nombre')
