from django.db import models
from django.conf import settings
from mesas.models import Mesa
from menu.models import MenuItem

class Orden(models.Model):
    ESTADOS = [
        ('abierta',    'Abierta'),
        ('en_cocina',  'En cocina'),
        ('lista',      'Lista'),
        ('cerrada',    'Cerrada'),
        ('cancelada',  'Cancelada'),
    ]
    mesa        = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='ordenes')
    mozo        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, related_name='ordenes')
    estado      = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    creada_en   = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Orden #{self.id} — Mesa {self.mesa.numero} ({self.estado})"


class ItemOrden(models.Model):
    orden       = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    menu_item   = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    cantidad    = models.PositiveIntegerField(default=1)
    nota        = models.CharField(max_length=200, blank=True)  # ej: "sin cebolla"

    @property
    def subtotal(self):
        return self.cantidad * self.menu_item.precio

    def __str__(self):
        return f"{self.cantidad}x {self.menu_item.nombre}"