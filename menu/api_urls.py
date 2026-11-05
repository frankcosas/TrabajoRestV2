from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import CategoriaViewSet, LoginTokenView, PlatoViewSet

router = DefaultRouter()
router.register('platos', PlatoViewSet, basename='api-plato')
router.register('categorias', CategoriaViewSet, basename='api-categoria')

urlpatterns = [
    path('token/', LoginTokenView.as_view(), name='api-token'),
    path('', include(router.urls)),
]
