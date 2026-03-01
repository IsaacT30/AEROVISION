# leads/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Lead
from .serializers import LeadSerializer, LeadCreateSerializer


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para leads/consultas
    POST: público (cualquiera puede enviar una consulta)
    GET/PUT/DELETE: solo admin
    """
    queryset = Lead.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        return LeadSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Crear un nuevo lead (público)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        
        return Response(
            LeadSerializer(lead).data,
            status=status.HTTP_201_CREATED
        )
