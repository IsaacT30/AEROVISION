# services/serializers.py
from rest_framework import serializers
from django.utils.text import slugify
from django.core.files.base import ContentFile
import base64
import uuid
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = (
            'id', 'nombre', 'slug', 'categoria', 'categoria_display',
            'descripcion', 'imagen', 'imagen_url', 'precio_base', 'precio_por_hora', 'horas_minimas',
            'activo', 'orden', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'categoria_display', 'imagen_url')
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)
    imagen = serializers.ImageField(required=False, allow_null=True)
    imagen_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    precio_por_hora = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)
    horas_minimas = serializers.IntegerField(default=1, required=False)
    activo = serializers.BooleanField(default=True, required=False)
    orden = serializers.IntegerField(default=0, required=False)
    
    class Meta:
        model = Service
        fields = (
            'nombre', 'slug', 'categoria', 'descripcion', 'imagen', 'imagen_base64',
            'precio_base', 'precio_por_hora', 'horas_minimas',
            'activo', 'orden'
        )
    
    def validate(self, data):
        # Procesar imagen base64 si viene
        imagen_base64 = data.pop('imagen_base64', None)
        if imagen_base64:
            # Verificar si es una URL de data (data:image/jpeg;base64,...)
            if imagen_base64.startswith('data:image'):
                # Extraer el formato y los datos
                format_prefix, imgstr = imagen_base64.split(';base64,')
                ext = format_prefix.split('/')[-1]
                
                # Decodificar base64
                img_data = base64.b64decode(imgstr)
                
                # Generar nombre único para la imagen
                filename = f"{uuid.uuid4()}.{ext}"
                
                # Crear archivo
                data['imagen'] = ContentFile(img_data, name=filename)
        
        # Generar slug automáticamente si no viene
        if not data.get('slug'):
            nombre = data.get('nombre', '')
            base_slug = slugify(nombre)
            slug = base_slug
            counter = 1
            
            # Asegurarse de que el slug sea único
            # En update, excluir el objeto actual
            exclude_id = self.instance.id if self.instance else None
            queryset = Service.objects.all()
            if exclude_id:
                queryset = queryset.exclude(id=exclude_id)
            
            while queryset.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            data['slug'] = slug
        
        return data
