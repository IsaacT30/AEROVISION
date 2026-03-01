# bookings/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking
from services.models import Service
from .serializers import (
    BookingListSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    DisponibilidadQuerySerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas
    - Cualquiera puede crear una reserva (queda en PENDIENTE)
    - Solo admin puede ver todas las reservas
    - Solo admin puede confirmar/cancelar
    """
    queryset = Booking.objects.select_related('servicio').all()
    permission_classes = (permissions.AllowAny,)  # Lectura pública para calendario
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ('update', 'partial_update'):
            return BookingUpdateSerializer
        return BookingListSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Filtros opcionales por query params
        fecha = self.request.query_params.get('fecha')
        servicio_id = self.request.query_params.get('servicio')
        estado = self.request.query_params.get('estado')
        
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                qs = qs.filter(fecha=fecha_obj)
            except ValueError:
                pass
        
        if servicio_id:
            qs = qs.filter(servicio_id=servicio_id)
        
        if estado:
            qs = qs.filter(estado=estado)
        
        return qs
    
    def create(self, request, *args, **kwargs):
        """
        Crear una nueva reserva (estado PENDIENTE por defecto)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Guardar con estado PENDIENTE
        booking = serializer.save(estado='PENDIENTE')
        
        return Response(
            BookingListSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Solo admin puede actualizar reservas
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Solo administradores pueden modificar reservas'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Solo admin puede actualizar parcialmente reservas
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Solo administradores pueden modificar reservas'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Solo admin puede eliminar reservas
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Solo administradores pueden eliminar reservas'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verificar_disponibilidad(self, request):
        """
        Endpoint para verificar disponibilidad antes de crear una reserva
        POST /api/bookings/verificar_disponibilidad/
        Body: {
            "servicio_id": 1,
            "fecha": "2026-03-15",
            "hora_inicio": "14:00",
            "hora_fin": "17:00"
        }
        """
        serializer = DisponibilidadQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            servicio = Service.objects.get(id=data['servicio_id'], activo=True)
        except Service.DoesNotExist:
            return Response({'error': 'Servicio no encontrado'}, status=404)
        
        # Crear instancia temporal
        temp_booking = Booking(
            servicio=servicio,
            fecha=data['fecha'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin']
        )
        
        conflictos = temp_booking.verificar_disponibilidad()
        
        if conflictos:
            return Response({
                'disponible': False,
                'mensaje': 'El horario NO está disponible',
                'conflictos': [
                    {
                        'id': c.id,
                        'fecha': c.fecha,
                        'hora_inicio': c.hora_inicio,
                        'hora_fin': c.hora_fin,
                        'cliente': c.cliente_nombre
                    }
                    for c in conflictos
                ]
            })
        
        # Calcular precio estimado
        horas = temp_booking.calcular_horas()
        es_fin_de_semana = data['fecha'].weekday() >= 5
        precio = servicio.calcular_precio(horas, es_fin_de_semana, False)
        
        return Response({
            'disponible': True,
            'mensaje': 'El horario está disponible',
            'horas': horas,
            'precio_estimado': float(precio),
            'es_fin_de_semana': es_fin_de_semana
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def calendario_ocupado(self, request):
        """
        Endpoint para obtener fechas/horarios ocupados para el calendario del frontend
        GET /api/bookings/calendario_ocupado/?servicio=1&mes=2026-03
        """
        servicio_id = request.query_params.get('servicio')
        mes_str = request.query_params.get('mes')  # Formato: YYYY-MM
        
        if not servicio_id:
            return Response({'error': 'Se requiere servicio_id'}, status=400)
        
        qs = Booking.objects.filter(
            servicio_id=servicio_id,
            estado__in=['PENDIENTE', 'CONFIRMADO']
        )
        
        # Filtrar por mes si se proporciona
        if mes_str:
            try:
                year, month = map(int, mes_str.split('-'))
                qs = qs.filter(fecha__year=year, fecha__month=month)
            except ValueError:
                pass
        
        # Agrupar por fecha
        fechas_ocupadas = {}
        for booking in qs:
            fecha_str = booking.fecha.isoformat()
            if fecha_str not in fechas_ocupadas:
                fechas_ocupadas[fecha_str] = []
            
            fechas_ocupadas[fecha_str].append({
                'id': booking.id,
                'hora_inicio': booking.hora_inicio.strftime('%H:%M'),
                'hora_fin': booking.hora_fin.strftime('%H:%M'),
                'cliente': booking.cliente_nombre,
                'estado': booking.estado
            })
        
        return Response({
            'servicio_id': int(servicio_id),
            'fechas_ocupadas': fechas_ocupadas
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def confirmar(self, request, pk=None):
        """
        Confirmar una reserva (solo admin)
        POST /api/bookings/{id}/confirmar/
        """
        booking = self.get_object()
        
        if booking.estado == 'CANCELADO':
            return Response({'error': 'No se puede confirmar una reserva cancelada'}, status=400)
        
        booking.estado = 'CONFIRMADO'
        booking.save(update_fields=['estado'])
        
        return Response(BookingListSerializer(booking).data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cancelar(self, request, pk=None):
        """
        Cancelar una reserva (solo admin)
        POST /api/bookings/{id}/cancelar/
        """
        booking = self.get_object()
        booking.estado = 'CANCELADO'
        booking.save(update_fields=['estado'])
        
        return Response(BookingListSerializer(booking).data)
