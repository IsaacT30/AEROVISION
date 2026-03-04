# portafolio/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from services.permissions import IsAdminOrReadOnly
from .models import Portafolio
from .serializers import PortafolioSerializer


class PortafolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el portafolio
    GET: público
    POST/PUT/DELETE: Temporal AllowAny para desarrollo (cambiar a IsAdminOrReadOnly en producción)
    """
    queryset = Portafolio.objects.all()
    serializer_class = PortafolioSerializer
    permission_classes = (AllowAny,)  # Temporal para desarrollo
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    ordering_fields = ('orden', 'created_at')
    
    def create(self, request, *args, **kwargs):
        """Override para debugging"""
        print("=" * 50)
        print("DATOS RECIBIDOS:")
        print(f"request.data: {request.data}")
        print(f"request.POST: {request.POST}")
        print("=" * 50)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("ERRORES DE VALIDACION:")
            print(serializer.errors)
            print("=" * 50)
        
        return super().create(request, *args, **kwargs)
    
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
