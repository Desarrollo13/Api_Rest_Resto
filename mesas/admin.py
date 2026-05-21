from django.contrib import admin
from mesas.models import Mesa,Reserva


# Register your models here.
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display=['numero','capacidad','estado']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):   
    list_display=['mesa','cliente_nombre','cliente_telefono','fecha_hora','personas','confirmada'] 
