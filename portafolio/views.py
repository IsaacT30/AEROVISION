# portafolio/views.py
from rest_framework import viewsets, filters
from services.permissions import IsAdminOrReadOnly
from .models import Portafolio
from .serializers import PortafolioSerializer


class PortafolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el portafolio
    GET: público
    POST/PUT/DELETE: solo admin
    """
    queryset = Portafolio.objects.all()
    serializer_class = PortafolioSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    ordering_fields = ('orden', 'created_at')
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Si no es admin, solo mostrar activos
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(activo=True)
        
        # Filtros opcionales
        categoria = self.request.query_params.get('categoria')
        tipo = self.request.query_params.get('tipo')
        
        if categoria:
            qs = qs.filter(categoria=categoria)
        if tipo:
            qs = qs.filter(tipo=tipo)
        
        return qs
