# portafolio/serializers.py
from rest_framework import serializers
from .models import Portafolio


class PortafolioSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # Alias para compatibilidad con el frontend
    tipo_medio = serializers.CharField(source='tipo', read_only=True)
    url_medio = serializers.CharField(source='imagen', read_only=True)
    destacado = serializers.BooleanField(source='destacado_en_portada', read_only=True)
    
    class Meta:
        model = Portafolio
        fields = (
            'id', 'titulo', 'categoria', 'categoria_display', 'tipo', 'tipo_display',
            'descripcion', 'ubicacion', 'enlace', 'imagen', 'destacado_en_portada',
            'activo', 'orden', 'created_at', 'updated_at',
            # Alias para el frontend
            'tipo_medio', 'url_medio', 'destacado'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_internal_value(self, data):
        """Normalizar y mapear campos del frontend"""
        # Crear una copia mutable de los datos
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Mapear campos del frontend al backend
        if 'tipo_medio' in data:
            data['tipo'] = data.pop('tipo_medio')
        
        if 'url_medio' in data:
            data['imagen'] = data.pop('url_medio')
        
        if 'destacado' in data:
            data['destacado_en_portada'] = data.pop('destacado')
        
        # Normalizar a mayúsculas
        if 'categoria' in data and data['categoria']:
            data['categoria'] = data['categoria'].upper()
        
        if 'tipo' in data and data['tipo']:
            data['tipo'] = data['tipo'].upper()
        
        return super().to_internal_value(data)
