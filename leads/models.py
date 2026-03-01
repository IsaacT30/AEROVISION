# leads/models.py
from django.db import models


class Lead(models.Model):
    """
    Modelo para formulario de contacto / cotización sin compromiso
    """
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    servicio_interes = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Servicio en el que está interesado"
    )
    mensaje = models.TextField(help_text="Mensaje o consulta del cliente")
    
    # Metadata
    leido = models.BooleanField(default=False, help_text="Marcado por el admin")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Lead / Consulta'
        verbose_name_plural = 'Leads / Consultas'
    
    def __str__(self):
        return f"{self.nombre} - {self.servicio_interes or 'General'} - {self.created_at.strftime('%Y-%m-%d')}"
