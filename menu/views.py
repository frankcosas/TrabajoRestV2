from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.views import LoginView
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PlatoForm, RegistroForm
from .models import Plato


# Inicio de sesión web: autentica con Django y genera/entrega el token REST.
class LoginConTokenView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        token, _ = Token.objects.get_or_create(user=form.get_user())
        # Se guarda en la sesión del usuario y se expone al frontend desde base.html.
        self.request.session['api_token'] = token.key
        return response


# Cierre de sesión: invalida el token en el servidor y cierra la sesión web.
@login_required
def logout_usuario(request):
    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        auth_logout(request)
    return redirect('home')


# Página principal (Home)
def home(request):
    return render(request, 'menu/home.html')


# Registro de usuarios nuevos
def registro(request):
    if request.user.is_authenticated:
        return redirect('lista_platos')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            request.session['api_token'] = token.key
            messages.success(request, f"Cuenta creada. ¡Bienvenido, {user.username}!")
            return redirect('lista_platos')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


# Listado de platos (requiere sesión iniciada)
@login_required
def lista_platos(request):
    platos = Plato.objects.select_related('categoria').all()
    return render(request, 'menu/lista_platos.html', {'platos': platos})


# Formulario para crear
@login_required
def crear_plato(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Plato creado correctamente.")
            return redirect('lista_platos')
    else:
        form = PlatoForm()
    return render(request, 'menu/crear_plato.html', {'form': form})


# Formulario para editar
@login_required
def editar_plato(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, "Plato actualizado correctamente.")
            return redirect('lista_platos')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'menu/editar_plato.html', {'form': form, 'plato': plato})


# Eliminar plato
@login_required
def eliminar_plato(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, "Plato eliminado correctamente.")
        return redirect('lista_platos')
    return render(request, 'menu/eliminar_plato.html', {'plato': plato})
