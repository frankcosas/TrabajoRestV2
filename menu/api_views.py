from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Categoria, Plato
from .serializers import CategoriaSerializer, PlatoSerializer


class LoginTokenView(ObtainAuthToken):
    """POST /api/token/  {"username": "...", "password": "..."}  ->  {"token": "..."}

    Si las credenciales son inválidas responde 400 con el detalle del error.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'username': user.username})


class PlatoViewSet(viewsets.ModelViewSet):
    """CRUD de platos.

    GET    /api/platos/       lista          GET    /api/platos/<id>/  detalle
    POST   /api/platos/       crea           PUT    /api/platos/<id>/  actualiza
    DELETE /api/platos/<id>/  elimina        (PATCH también disponible)
    """

    queryset = Plato.objects.all().order_by('id')
    serializer_class = PlatoSerializer
    permission_classes = [IsAuthenticated]


class CategoriaViewSet(viewsets.ModelViewSet):
    """CRUD de categorías (mismos métodos y permisos que platos)."""

    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
