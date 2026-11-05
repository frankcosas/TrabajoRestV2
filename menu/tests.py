from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from .models import Categoria, Plato


class AutenticacionWebTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('chef', 'chef@ejemplo.cl', 'ClaveSegura123')

    def test_vistas_protegidas_redirigen_al_login(self):
        plato = Plato.objects.create(nombre='Cazuela', precio=5000)
        urls = [
            reverse('lista_platos'), reverse('crear_plato'),
            reverse('editar_plato', args=[plato.pk]), reverse('eliminar_plato', args=[plato.pk]),
        ]
        for url in urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertIn(reverse('login'), r['Location'])

    def test_login_correcto_e_incorrecto(self):
        r = self.client.post(reverse('login'), {'username': 'chef', 'password': 'mala'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'incorrectos')
        r = self.client.post(reverse('login'), {'username': 'chef', 'password': 'ClaveSegura123'})
        self.assertRedirects(r, reverse('lista_platos'))
        token = Token.objects.get(user=self.user)
        self.assertEqual(self.client.session.get('api_token'), token.key)
        self.assertContains(self.client.get(reverse('lista_platos')), 'GOURMET_API_TOKEN')

    def test_logout(self):
        self.client.login(username='chef', password='ClaveSegura123')
        r = self.client.post(reverse('logout'))
        self.assertRedirects(r, reverse('home'))
        self.assertEqual(self.client.get(reverse('lista_platos')).status_code, 302)

    def test_registro(self):
        r = self.client.post(reverse('registro'), {
            'username': 'nuevo', 'email': 'nuevo@ejemplo.cl',
            'password1': 'OtraClave12345', 'password2': 'OtraClave12345'})
        self.assertRedirects(r, reverse('lista_platos'))
        nuevo = User.objects.get(username='nuevo')
        self.assertTrue(Token.objects.filter(user=nuevo).exists())
        self.assertEqual(self.client.session.get('api_token'), Token.objects.get(user=nuevo).key)


class CrudWebTests(TestCase):
    def setUp(self):
        User.objects.create_user('chef', 'chef@ejemplo.cl', 'ClaveSegura123')
        self.client.login(username='chef', password='ClaveSegura123')

    def test_crud_completo(self):
        cat = Categoria.objects.create(nombre='Fondos')
        self.client.post(reverse('crear_plato'), {'nombre': 'Lomo saltado', 'precio': 9000, 'categoria': cat.pk, 'disponible': 'on'})
        plato = Plato.objects.get(nombre='Lomo saltado')
        self.assertEqual(plato.categoria, cat)
        self.client.post(reverse('editar_plato', args=[plato.pk]), {'nombre': 'Lomo saltado', 'precio': 9500})
        plato.refresh_from_db()
        self.assertEqual(plato.precio, 9500)
        self.client.post(reverse('eliminar_plato', args=[plato.pk]))
        self.assertFalse(Plato.objects.filter(pk=plato.pk).exists())

    def test_validaciones_no_guardan_datos_invalidos(self):
        casos = [
            {'nombre': '', 'precio': 1000},
            {'nombre': 'Plato123', 'precio': 1000},
            {'nombre': 'ab', 'precio': 1000},
            {'nombre': 'Cazuela', 'precio': 0},
            {'nombre': 'Cazuela', 'precio': -5},
            {'nombre': 'Cazuela', 'precio': 'abc'},
            {'nombre': 'Cazuela', 'precio': 2000000},
        ]
        for datos in casos:
            r = self.client.post(reverse('crear_plato'), datos)
            self.assertEqual(r.status_code, 200, datos)
            self.assertEqual(Plato.objects.count(), 0, datos)

    def test_nombre_duplicado(self):
        Plato.objects.create(nombre='Cazuela', precio=5000)
        self.client.post(reverse('crear_plato'), {'nombre': 'cazuela', 'precio': 6000})
        self.assertEqual(Plato.objects.count(), 1)

class ApiTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('chef', 'chef@ejemplo.cl', 'ClaveSegura123')

    def obtener_token(self):
        r = self.client.post('/api/token/', {'username': 'chef', 'password': 'ClaveSegura123'},
                             content_type='application/json')
        self.assertEqual(r.status_code, 200)
        return r.json()['token']

    def test_login_devuelve_token(self):
        self.assertTrue(Token.objects.filter(key=self.obtener_token(), user=self.user).exists())

    def test_login_invalido(self):
        r = self.client.post('/api/token/', {'username': 'chef', 'password': 'mala'},
                             content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_sin_token_401(self):
        self.assertEqual(self.client.get('/api/platos/').status_code, 401)

    def test_token_invalido_401(self):
        r = self.client.get('/api/platos/', HTTP_AUTHORIZATION='Token inventado')
        self.assertEqual(r.status_code, 401)


class ApiPlatosTests(TestCase):
    def setUp(self):
        User.objects.create_user('chef', 'chef@ejemplo.cl', 'ClaveSegura123')
        r = self.client.post('/api/token/', {'username': 'chef', 'password': 'ClaveSegura123'},
                             content_type='application/json')
        self.auth = {'HTTP_AUTHORIZATION': 'Token ' + r.json()['token']}

    def test_get_lista_y_detalle(self):
        p = Plato.objects.create(nombre='Cazuela', precio=5000)
        r = self.client.get('/api/platos/', **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)
        r = self.client.get(f'/api/platos/{p.pk}/', **self.auth)
        self.assertEqual(r.json()['nombre'], 'Cazuela')

    def test_post_crea(self):
        r = self.client.post('/api/platos/', {'nombre': 'Pastel de choclo', 'precio': 7000},
                             content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Plato.objects.filter(nombre='Pastel de choclo').exists())

    def test_put_actualiza(self):
        p = Plato.objects.create(nombre='Cazuela', precio=5000)
        r = self.client.put(f'/api/platos/{p.pk}/', {'nombre': 'Cazuela', 'precio': 5500, 'disponible': False},
                            content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 200)
        p.refresh_from_db()
        self.assertEqual((p.precio, p.disponible), (5500, False))

    def test_delete_elimina(self):
        p = Plato.objects.create(nombre='Cazuela', precio=5000)
        r = self.client.delete(f'/api/platos/{p.pk}/', **self.auth)
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Plato.objects.filter(pk=p.pk).exists())

    def test_inexistente_404(self):
        for metodo in ('get', 'delete'):
            r = getattr(self.client, metodo)('/api/platos/9999/', **self.auth)
            self.assertEqual(r.status_code, 404)
        r = self.client.put('/api/platos/9999/', {'nombre': 'Algo', 'precio': 1},
                            content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 404)

    def test_datos_invalidos_400(self):
        casos = [{'nombre': '', 'precio': 1000}, {'nombre': 'Plato123', 'precio': 1000},
                 {'nombre': 'Cazuela', 'precio': 0}, {'nombre': 'Cazuela', 'precio': 'abc'},
                 {'precio': 1000}]
        for datos in casos:
            r = self.client.post('/api/platos/', datos, content_type='application/json', **self.auth)
            self.assertEqual(r.status_code, 400, datos)
        self.assertEqual(Plato.objects.count(), 0)

    def test_json_malformado_400(self):
        r = self.client.post('/api/platos/', '{mal', content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 400)


class ApiIntegracionTests(TestCase):
    """La API y la web comparten modelos: lo creado por una se ve en la otra."""

    def setUp(self):
        User.objects.create_user('chef', 'chef@ejemplo.cl', 'ClaveSegura123')
        r = self.client.post('/api/token/', {'username': 'chef', 'password': 'ClaveSegura123'},
                             content_type='application/json')
        self.auth = {'HTTP_AUTHORIZATION': 'Token ' + r.json()['token']}

    def test_plato_creado_por_api_aparece_en_la_web(self):
        cat = self.client.post('/api/categorias/', {'nombre': 'Postres'},
                               content_type='application/json', **self.auth).json()
        r = self.client.post('/api/platos/', {'nombre': 'Leche asada', 'precio': 3000, 'categoria': cat['id']},
                             content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 201)
        self.client.login(username='chef', password='ClaveSegura123')
        self.assertContains(self.client.get(reverse('lista_platos')), 'Leche asada')

    def test_validaciones_api_reglas_de_negocio(self):
        Plato.objects.create(nombre='Cazuela', precio=5000)
        casos = [{'nombre': 'cazuela', 'precio': 1000},       # duplicado
                 {'nombre': 'ab', 'precio': 1000},            # muy corto
                 {'nombre': 'Cazuela2', 'precio': 1000},      # con numeros
                 {'nombre': 'Asado', 'precio': 2000000},      # sobre el maximo
                 {'nombre': 'Asado', 'precio': 1000, 'categoria': 999}]  # categoria inexistente
        for datos in casos:
            r = self.client.post('/api/platos/', datos, content_type='application/json', **self.auth)
            self.assertEqual(r.status_code, 400, datos)
        self.assertEqual(Plato.objects.count(), 1)

    def test_crud_categorias(self):
        r = self.client.post('/api/categorias/', {'nombre': 'Entradas'}, content_type='application/json', **self.auth)
        pk = r.json()['id']
        r = self.client.put(f'/api/categorias/{pk}/', {'nombre': 'Entradas frias'}, content_type='application/json', **self.auth)
        self.assertEqual(r.json()['nombre'], 'Entradas frias')
        self.assertEqual(self.client.delete(f'/api/categorias/{pk}/', **self.auth).status_code, 204)
