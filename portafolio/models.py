# portafolio/models.py
from django.db import models


class Portafolio(models.Model):
    """
    Modelo para el portafolio de trabajos realizados
    """
    CATEGORIA_CHOICES = [
        ('EVENTOS', 'Eventos'),
        ('INMOBILIARIO', 'Bienes Raíces'),
        ('TURISMO', 'Turismo'),
        ('INSPECCION', 'Inspecciones'),
        ('PRODUCCION', 'Producción Audiovisual'),
    ]
    
    TIPO_CHOICES = [
        ('FOTO', 'Fotografía'),
        ('VIDEO', 'Video'),
    ]
    
    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    destacado_en_portada = models.BooleanField(default=False, help_text="Mostrar en la portada principal")
    
    # URL o archivo
    enlace = models.URLField(blank=True, help_text="YouTube, Vimeo, etc.")
    imagen = models.CharField(max_length=500, blank=True, help_text="URL de la imagen o video")
    
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('orden', '-created_at')
        verbose_name = 'Item de Portafolio'
        verbose_name_plural = 'Portafolio'
        db_table = 'portafolio_portafolio'
    
    def __str__(self):
        return f"{self.titulo} - {self.get_categoria_display()}"
