from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import painel
# Create your views here.

def index(request):
    return(HttpResponse("teste"))

def showPainel(request,campus):

    return painel.painel(request,campus)
