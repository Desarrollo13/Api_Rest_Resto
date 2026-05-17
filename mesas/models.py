from django.db import models

# Create your models here.
class Mesa(models.Model):
    ESTADOS=[
        ('disponible','Disponible'),
        ('ocupado','Ocupado'),
        ('reservado','Reservado'),        
    ]
    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=20,choices=ESTADOS,default='disponible')
    def __str__(self):
        return f"Mesa {self.numero} - {self.estado}"
    

class Reserva(models.Model):
    mesa = models.ForeignKey(Mesa,on_delete=models.CASCADE,related_name='reservas')
    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField()
    personas = models.PositiveIntegerField()
    confirmada = models.BooleanField(default=False)
    def __str__(self):
        return f"Reserva {self.cliente_nombre} — Mesa {self.mesa.numero}"