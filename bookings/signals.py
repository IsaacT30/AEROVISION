# bookings/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Booking


@receiver(pre_save, sender=Booking)
def calculate_total(sender, instance, **kwargs):
    """
    Calcula automáticamente el total_cotizado antes de guardar
    si aún no tiene valor
    """
    if instance.total_cotizado is None and instance.servicio:
        horas = instance.calcular_horas()
        # Determinar si es fin de semana
        es_fin_de_semana = instance.fecha.weekday() >= 5 if instance.fecha else False
        # Por ahora sin lógica de feriados
        es_feriado = False
        
        instance.total_cotizado = instance.servicio.calcular_precio(
            horas, es_fin_de_semana, es_feriado
        )
