# services/serializers.py
from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Service
        fields = (
            'id', 'nombre', 'slug', 'categoria', 'categoria_display',
            'descripcion', 'precio_base', 'precio_por_hora', 'horas_minimas',
            'activo', 'orden', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'categoria_display')


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'nombre', 'slug', 'categoria', 'descripcion',
            'precio_base', 'precio_por_hora', 'horas_minimas',
            'activo', 'orden'
        )
