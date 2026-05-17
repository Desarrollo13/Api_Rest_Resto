from rest_framework import serializers
from menu.models import Categoria, MenuItem

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class MenuItemSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = MenuItem
        fields = ['id', 'categoria', 'categoria_nombre', 'nombre',
                  'descripcion', 'precio', 'disponible', 'imagen']