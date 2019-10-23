from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import painelCampus
# Create your views here.

def index(request):
    return(HttpResponse("teste"))

def showPainelCampus(request,campus):

    return painelCampus.painel(request,campus)
