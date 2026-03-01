# bookings/admin.py
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'servicio', 'fecha', 'hora_inicio', 'hora_fin',
        'cliente_nombre', 'cliente_telefono', 'estado', 'total_cotizado', 'created_at'
    )
    list_filter = ('estado', 'servicio', 'fecha')
    search_fields = ('cliente_nombre', 'cliente_telefono', 'cliente_email')
    readonly_fields = ('created_at', 'updated_at', 'total_cotizado')
    ordering = ('-fecha', '-hora_inicio')
    
    fieldsets = (
        ('Servicio', {
            'fields': ('servicio', 'fecha', 'hora_inicio', 'hora_fin')
        }),
        ('Cliente', {
            'fields': ('cliente_nombre', 'cliente_telefono', 'cliente_email', 'ciudad')
        }),
        ('Detalles', {
            'fields': ('mensaje', 'estado', 'total_cotizado')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Override para mostrar errores de validación en el admin
        """
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f'Error: {str(e)}', level='error')
            raise
