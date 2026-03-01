# leads/serializers.py
from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'id', 'nombre', 'telefono', 'email', 'ciudad',
            'servicio_interes', 'mensaje', 'leido', 'created_at'
        )
        read_only_fields = ('id', 'leido', 'created_at')


class LeadCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear leads (público)"""
    class Meta:
        model = Lead
        fields = ('nombre', 'telefono', 'email', 'ciudad', 'servicio_interes', 'mensaje')
