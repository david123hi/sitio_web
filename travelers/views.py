from django.shortcuts import render
from .models import Viaje
from .models import Participacion
from .models import Viajero

def lista_viajes(request):
    viajes = Viaje.objects.all()
    contexto = {
        'viajes': viajes
    }
    return render(request, 'travelers_Main.html', contexto)

def detalle_viaje(request, viaje_id):
    viaje = Viaje.objects.get(id=viaje_id)
    participaciones = Participacion.objects.filter(viaje=viaje).select_related('viajero')
    contexto = {
        'viaje': viaje,
        'participaciones': participaciones
    }
    return render(request, 'travelers_Details.html', contexto)

def detalle_viajeros(request):
    viajeros = Viajero.objects.all()
    contexto = {
        'viajeros': viajeros
    }
    return render(request, 'travelers_Manage.html', contexto)
