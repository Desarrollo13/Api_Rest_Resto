from django.contrib import admin
from ordenes.models import Orden,ItemOrden

# Register your models here.
@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display=['mesa','mozo','estado','creada_en','actualizada']
@admin.register(ItemOrden)
class ItemOrden(admin.ModelAdmin):
    list_display=['orden','menu_item','cantidad','nota']    
