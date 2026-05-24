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
#modelo de pago
# ordenes/models.py  — agregá esto al archivo existente

class Pago(models.Model):
    METODOS = [
        ('efectivo',      'Efectivo'),
        ('tarjeta',       'Tarjeta de crédito/débito'),
        ('transferencia', 'Transferencia bancaria'),
    ]
    ESTADOS = [
        ('pendiente',  'Pendiente'),
        ('completado', 'Completado'),
        ('rechazado',  'Rechazado'),
    ]

    orden           = models.OneToOneField(Orden, on_delete=models.PROTECT, related_name='pago')
    metodo_pago     = models.CharField(max_length=20, choices=METODOS)
    estado          = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total           = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recibido  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # para efectivo
    vuelto          = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cajero          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, related_name='pagos')
    fecha           = models.DateTimeField(auto_now_add=True)
    referencia      = models.CharField(max_length=100, blank=True)  # nro de transacción para tarjeta/transferencia

    def __str__(self):
        return f"Pago #{self.id} — Orden #{self.orden.id} ({self.metodo_pago})"
 