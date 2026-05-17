from django.db import models

class Categoria(models.Model):
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class MenuItem(models.Model):
    categoria   = models.ForeignKey(Categoria, on_delete=models.SET_NULL,
                                    null=True, related_name='items')
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio      = models.DecimalField(max_digits=8, decimal_places=2)
    disponible  = models.BooleanField(default=True)
    imagen      = models.ImageField(upload_to='menu/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"