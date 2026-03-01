# portafolio/serializers.py
from rest_framework import serializers
from .models import Portafolio


class PortafolioSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Portafolio
        fields = (
            'id', 'titulo', 'categoria', 'categoria_display', 'tipo', 'tipo_display',
            'descripcion', 'ubicacion', 'enlace', 'imagen', 'activo', 'orden',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
