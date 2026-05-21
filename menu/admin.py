from django.contrib import admin
from menu.models import Categoria,MenuItem

# Register your models here.
@admin.register(Categoria)
class CatagoriaAdmin(admin.ModelAdmin):
    list_display=['nombre','descripcion']
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display=['categoria','nombre','descripcion','precio','disponible','imagen']