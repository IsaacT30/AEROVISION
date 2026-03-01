# bookings/models.py
from django.db import models
from django.core.exceptions import ValidationError
from services.models import Service
from datetime import datetime, time


class Booking(models.Model):
    """
    Modelo para las reservas/agendamiento de servicios
    IMPORTANTE: Valida que no haya solapamiento de horarios
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Relación con servicio
    servicio = models.ForeignKey(
        Service, 
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    
    # Información de fecha y hora
    fecha = models.DateField(help_text="Fecha de la reserva")
    hora_inicio = models.TimeField(help_text="Hora de inicio (ej: 14:00)")
    hora_fin = models.TimeField(help_text="Hora de fin (ej: 17:00)")
    
    # Cliente
    cliente_nombre = models.CharField(max_length=200)
    cliente_telefono = models.CharField(max_length=20)
    cliente_email = models.EmailField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    
    # Detalles
    mensaje = models.TextField(blank=True, help_text="Notas o requerimientos especiales")
    estado = models.CharField(
        max_length=15, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE'
    )
    
    # Precio calculado (se guarda para histórico)
    total_cotizado = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total calculado al momento de la reserva"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-fecha', '-hora_inicio')
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        indexes = [
            models.Index(fields=['fecha', 'hora_inicio']),
            models.Index(fields=['servicio', 'fecha']),
        ]
    
    def __str__(self):
        return f"Reserva {self.id} - {self.cliente_nombre} - {self.fecha} {self.hora_inicio}"
    
    def clean(self):
        """
        Validación crucial: detecta solapamiento de horarios
        """
        super().clean()
        
        # Validar que hora_fin sea mayor que hora_inicio
        if self.hora_inicio and self.hora_fin:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
                })
        
        # Validar que no haya solapamiento con otras reservas
        if self.fecha and self.hora_inicio and self.hora_fin:
            reservas_conflictivas = self.verificar_disponibilidad()
            if reservas_conflictivas:
                raise ValidationError(
                    f'Ya existe una reserva en ese horario. '
                    f'Conflictos con: {", ".join([str(r.id) for r in reservas_conflictivas])}'
                )
    
    def verificar_disponibilidad(self):
        """
        Verifica si hay solapamiento con otras reservas
        Regla: Hay choque si:
            - Misma fecha
            - Estado es PENDIENTE o CONFIRMADO
            - Los rangos de tiempo se cruzan:
              inicio < fin_existente AND fin > inicio_existente
        """
        # Excluir la reserva actual si está actualizando
        qs = Booking.objects.filter(
            fecha=self.fecha,
            servicio=self.servicio,
            estado__in=['PENDIENTE', 'CONFIRMADO']
        )
        
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        
        # Detectar solapamiento de horarios
        conflictos = []
        for reserva in qs:
            # Hay solapamiento si:
            # self.hora_inicio < reserva.hora_fin AND self.hora_fin > reserva.hora_inicio
            if self.hora_inicio < reserva.hora_fin and self.hora_fin > reserva.hora_inicio:
                conflictos.append(reserva)
        
        return conflictos
    
    def save(self, *args, **kwargs):
        # Ejecutar validación antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calcular_horas(self):
        """
        Calcula la cantidad de horas entre hora_inicio y hora_fin
        """
        if not self.hora_inicio or not self.hora_fin:
            return 0
        
        inicio = datetime.combine(self.fecha, self.hora_inicio)
        fin = datetime.combine(self.fecha, self.hora_fin)
        diferencia = fin - inicio
        horas = diferencia.total_seconds() / 3600
        return round(horas, 2)
