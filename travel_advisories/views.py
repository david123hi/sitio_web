from django.shortcuts import render
from .models import Alerta
# Create your views here.

def lista_alerta(request):
    alertas = Alerta.objects.all()
    contexto = {
        'alertas': alertas
    }
    return render(request, 'advisories_Main.html', contexto)