# leads/admin.py
from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'servicio_interes', 'ciudad', 'leido', 'created_at')
    list_filter = ('leido', 'created_at', 'servicio_interes')
    search_fields = ('nombre', 'telefono', 'email', 'mensaje')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(leido=True)
    mark_as_read.short_description = "Marcar como leído"
    
    actions = [mark_as_read]
