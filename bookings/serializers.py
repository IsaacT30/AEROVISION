# bookings/serializers.py
from rest_framework import serializers
from .models import Booking
from services.models import Service
from datetime import datetime, time


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer para listar reservas"""
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    horas_totales = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = (
            'id', 'servicio', 'servicio_nombre', 'fecha', 'hora_inicio', 'hora_fin',
            'cliente_nombre', 'cliente_telefono', 'cliente_email', 'ciudad',
            'estado', 'estado_display', 'total_cotizado', 'horas_totales',
            'mensaje', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'servicio_nombre', 'estado_display')
    
    def get_horas_totales(self, obj):
        return obj.calcular_horas()


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reservas con validación de disponibilidad"""
    servicio_id = serializers.PrimaryKeyRelatedField(
        source='servicio',
        queryset=Service.objects.filter(activo=True),
        write_only=True
    )
    
    class Meta:
        model = Booking
        fields = (
            'servicio_id', 'fecha', 'hora_inicio', 'hora_fin',
            'cliente_nombre', 'cliente_telefono', 'cliente_email',
            'ciudad', 'mensaje'
        )
    
    def validate(self, attrs):
        """
        Validación adicional de disponibilidad
        """
        fecha = attrs.get('fecha')
        hora_inicio = attrs.get('hora_inicio')
        hora_fin = attrs.get('hora_fin')
        servicio = attrs.get('servicio')
        
        # Validar que hora_fin > hora_inicio
        if hora_fin <= hora_inicio:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
            })
        
        # Crear instancia temporal para verificar disponibilidad
        temp_booking = Booking(
            servicio=servicio,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        
        conflictos = temp_booking.verificar_disponibilidad()
        if conflictos:
            raise serializers.ValidationError({
                'non_field_errors': [
                    f'El horario no está disponible. Ya existe una reserva en ese rango de tiempo. '
                    f'Reservas conflictivas: {", ".join([str(c.id) for c in conflictos])}'
                ]
            })
        
        return attrs


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar reservas (solo ciertos campos)"""
    class Meta:
        model = Booking
        fields = (
            'cliente_nombre', 'cliente_telefono', 'cliente_email',
            'ciudad', 'mensaje', 'estado'
        )


class DisponibilidadQuerySerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad"""
    fecha = serializers.DateField(required=True)
    hora_inicio = serializers.TimeField(required=True)
    hora_fin = serializers.TimeField(required=True)
    servicio_id = serializers.IntegerField(required=True)
    
    def validate(self, attrs):
        if attrs['hora_fin'] <= attrs['hora_inicio']:
            raise serializers.ValidationError('La hora de fin debe ser posterior a la hora de inicio')
        return attrs
