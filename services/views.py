# services/views.py
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from .models import Service
from .serializers import ServiceSerializer, ServiceCreateUpdateSerializer
from .permissions import IsAdminOrReadOnly


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar servicios de AeroVisión
    GET: público
    POST/PUT/PATCH/DELETE: solo admin
    """
    queryset = Service.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('nombre', 'descripcion', 'categoria')
    ordering_fields = ('nombre', 'precio_base', 'orden', 'created_at')
    lookup_field = 'slug'
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Si no es admin, solo mostrar servicios activos
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(activo=True)
        
        # Filtro opcional por categoría
        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)
        
        return qs
    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ServiceCreateUpdateSerializer
        return ServiceSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def cotizar(self, request, slug=None):
        """
        Endpoint para cotizar un servicio
        POST /api/services/{slug}/cotizar/
        Body: { "fecha": "2026-03-15", "horas": 3 }
        """
        service = self.get_object()
        
        fecha_str = request.data.get('fecha')
        horas = request.data.get('horas', 1)
        
        if not fecha_str:
            return Response({'error': 'Se requiere la fecha'}, status=400)
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            horas = int(horas)
        except (ValueError, TypeError):
            return Response({'error': 'Formato inválido. Use fecha: YYYY-MM-DD, horas: número'}, status=400)
        
        # Determinar si es fin de semana (sábado=5, domingo=6)
        es_fin_de_semana = fecha.weekday() >= 5
        
        # TODO: Implementar lógica de feriados
        es_feriado = False
        
        # Calcular precio
        horas_cobrables = max(horas, service.horas_minimas)
        precio_total = service.calcular_precio(horas, es_fin_de_semana, es_feriado)
        
        # Desglose
        precio_base = float(service.precio_base)
        precio_horas = float(service.precio_por_hora * horas_cobrables)
        recargo_fin_semana = 0.15 if es_fin_de_semana else 0
        recargo_feriado = 0.25 if es_feriado else 0
        
        return Response({
            'servicio': service.nombre,
            'fecha': fecha_str,
            'horas_solicitadas': horas,
            'horas_cobrables': horas_cobrables,
            'es_fin_de_semana': es_fin_de_semana,
            'es_feriado': es_feriado,
            'desglose': {
                'precio_base': precio_base,
                'precio_horas': precio_horas,
                'recargo_fin_semana': f"{recargo_fin_semana * 100}%",
                'recargo_feriado': f"{recargo_feriado * 100}%",
            },
            'total': float(precio_total)
        })
