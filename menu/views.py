from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PlatoForm, RegistroForm
from .models import Plato


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
