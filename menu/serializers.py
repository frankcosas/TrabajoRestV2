from rest_framework import serializers

from .models import Categoria, Plato


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class PlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plato
        fields = ['id', 'nombre', 'descripcion', 'precio', 'categoria', 'disponible']

    def validate_nombre(self, value):
        value = value.strip()
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("El nombre debe contener letras válidas.")
        # Regla de negocio: no repetir platos (sin distinguir mayúsculas)
        duplicados = Plato.objects.filter(nombre__iexact=value)
        if self.instance is not None:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise serializers.ValidationError("Ya existe un plato con ese nombre.")
        return value

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser un número positivo mayor que 0.")
        return value
