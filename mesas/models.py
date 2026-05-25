# mesas/models.py
from django.db import models
from django.conf import settings

class Mesa(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('ocupada',    'Ocupada'),
        ('reservada',  'Reservada'),
    ]
    numero    = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()
    estado    = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return f"Mesa {self.numero} — {self.estado}"


class Reserva(models.Model):
    ESTADOS = [
        ('pendiente',   'Pendiente'),
        ('confirmada',  'Confirmada'),
        ('cancelada',   'Cancelada'),
        ('completada',  'Completada'),
    ]
    mesa             = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='reservas')
    cliente_nombre   = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20)
    fecha_hora       = models.DateTimeField()
    personas         = models.PositiveIntegerField()
    estado           = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creada_por       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, related_name='reservas_creadas')
    notas            = models.TextField(blank=True)
    creada_en        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.cliente_nombre} — Mesa {self.mesa.numero} ({self.fecha_hora})"