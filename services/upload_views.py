# services/upload_views.py
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.conf import settings
import os


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Endpoint genérico para subir archivos
    POST /api/upload/
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No se encontró ningún archivo en la petición'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Validar tipo de archivo (imágenes)
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_ext = os.path.splitext(file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response(
            {'error': f'Tipo de archivo no permitido. Use: {", ".join(allowed_extensions)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar tamaño (máx 5MB)
    if file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'El archivo es demasiado grande. Máximo 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Guardar archivo
    try:
        folder = request.data.get('folder', 'uploads')
        filename = default_storage.save(f'{folder}/{file.name}', file)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
        
        return Response({
            'message': 'Archivo subido correctamente',
            'filename': filename,
            'url': file_url
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'Error al subir el archivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
