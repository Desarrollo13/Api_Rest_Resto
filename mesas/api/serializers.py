from rest_framework import serializers
from mesas.models import Mesa, Reserva
from django.utils import timezone

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mesa
        fields = ['id', 'numero', 'capacidad', 'estado']


class ReservaSerializer(serializers.ModelSerializer):
    mesa_numero    = serializers.ReadOnlyField(source='mesa.numero')
    creada_por_nombre = serializers.ReadOnlyField(source='creada_por.get_full_name')

    class Meta:
        model  = Reserva
        fields = [
            'id', 'mesa', 'mesa_numero', 'cliente_nombre',
            'cliente_telefono', 'fecha_hora', 'personas',
            'estado', 'notas', 'creada_por', 'creada_por_nombre',
            'creada_en'
        ]
        read_only_fields = ['creada_por', 'creada_en']

    def validate_fecha_hora(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'La fecha y hora de la reserva debe ser futura.'
            )
        return value

    def validate(self, data):
        mesa     = data.get('mesa')
        personas = data.get('personas')
        fecha    = data.get('fecha_hora')

        # Validar capacidad
        if personas and mesa and personas > mesa.capacidad:
            raise serializers.ValidationError({
                'personas': f'La mesa {mesa.numero} tiene capacidad para {mesa.capacidad} personas.'
            })

        # Validar que no haya otra reserva en el mismo horario (±2 horas)
        if mesa and fecha:
            from datetime import timedelta
            desde = fecha - timedelta(hours=2)
            hasta = fecha + timedelta(hours=2)
            reservas_existentes = Reserva.objects.filter(
                mesa=mesa,
                fecha_hora__range=(desde, hasta),
                estado__in=('pendiente', 'confirmada')
            )
            # Excluir la reserva actual en caso de edición
            if self.instance:
                reservas_existentes = reservas_existentes.exclude(pk=self.instance.pk)

            if reservas_existentes.exists():
                raise serializers.ValidationError(
                    f'La mesa {mesa.numero} ya tiene una reserva en ese horario.'
                )
        return data

    def create(self, validated_data):
        validated_data['creada_por'] = self.context['request'].user
        return super().create(validated_data)