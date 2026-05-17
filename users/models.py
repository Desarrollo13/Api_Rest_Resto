from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    ROLES=[
        ('administrador','Administrador'),
        ('gerente','Gerente'),
        ('mozo','Mozo'),
        ('cocinero','Cocinero'),
        ('cajero','Cajero'),
    ]
    rol = models.CharField(max_length=20,choices=ROLES)
    telefono =  models.CharField(max_length=20,blank=True)
    def __str__(self):
        return f"{self.get_full_name()}({self.rol})"
