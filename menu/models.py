from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator, RegexValidator
from django.db import models


solo_letras = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
    message="El nombre solo puede contener letras y espacios."
)


class Categoria(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(3, message="El nombre debe tener al menos 3 caracteres."), solo_letras],
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3, message="El nombre debe tener al menos 3 caracteres."), solo_letras]
    )
    descripcion = models.TextField(blank=True, max_length=500)
    precio = models.IntegerField(
        validators=[
            MinValueValidator(1, message="El precio debe ser mayor que 0."),
            MaxValueValidator(1000000, message="El precio no puede superar $1.000.000."),
        ]
    )
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='platos',
    )

    def __str__(self):
        return self.nombre
