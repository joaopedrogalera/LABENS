from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import painelCampus
from .models import Campus
# Create your views here.

def index(request):
    return render(request,'index.html')

def selectCampus(request):
    campi = Campus.objects.all()
    return render(request,'painelSelecCampus.html',{'campi':campi})

def showPainelCampus(request,campus):

    return painelCampus.painel(request,campus)
