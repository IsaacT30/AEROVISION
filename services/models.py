# services/models.py
from django.db import models
from decimal import Decimal


class Service(models.Model):
    """
    Modelo para los servicios que ofrece AeroVisión
    Ejemplos: Eventos, Bienes raíces, Turismo, Inspecciones, Producción audiovisual
    """
    CATEGORIA_CHOICES = [
        ('EVENTOS', 'Eventos'),
        ('INMOBILIARIO', 'Bienes Raíces'),
        ('TURISMO', 'Turismo'),
        ('INSPECCION', 'Inspecciones'),
        ('PRODUCCION', 'Producción Audiovisual'),
    ]
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)
    
    # Precios base
    precio_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Precio base del servicio"
    )
    precio_por_hora = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text="Precio adicional por hora"
    )
    horas_minimas = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad mínima de horas a cobrar"
    )
    
    # Configuración
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0, help_text="Orden de visualización")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('orden', 'nombre')
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return f"{self.nombre} - {self.get_categoria_display()}"
    
    def calcular_precio(self, horas, es_fin_de_semana=False, es_feriado=False):
        """
        Calcula el precio total del servicio
        """
        horas_cobrables = max(horas, self.horas_minimas)
        subtotal = self.precio_base + (Decimal(horas_cobrables) * self.precio_por_hora)
        
        # Aplicar recargos
        if es_fin_de_semana:
            subtotal *= Decimal('1.15')  # +15%
        
        if es_feriado:
            subtotal *= Decimal('1.25')  # +25%
        
        return round(subtotal, 2)
