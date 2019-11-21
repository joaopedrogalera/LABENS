from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import urlencode
from . import painelCampus
from .models import Campus
from django.views.decorators.csrf import csrf_exempt
import datetime
import ipaddress
# Create your views here.

def index(request):
    sessao = request.session.get('status', 0)

    if sessao:
        return render(request,'index.html')
    else:
        return redirect('/login?'+urlencode({'redirect':'/'}))

@csrf_exempt
def login(request):
    if request.method == 'GET':
        redir = ''
        if 'redirect' in request.GET:
            redir = request.GET['redirect']

        if ipaddress.IPv4Address(request.META['HTTP_X_FORWARDED_FOR'])>ipaddress.IPv4Address('200.134.0.0') and ipaddress.IPv4Address(request.META['HTTP_X_FORWARDED_FOR'])<ipaddress.IPv4Address('200.134.127.255'):
            request.session['status'] = 1
            if not redir == '':
                return redirect(redir)
            else:
                return redirect('/')

        return render(request,'login.html',{'redirect':redir,'loginErr':0})
    else:
        if not 'redirect' in request.POST or not 'passwd' in request.POST:
            return redirect('/login')

        if request.POST['passwd'] == 'Senha Aqui':
                request.session['status'] = 1
        else:
            return render(request,'login.html',{'redirect':request.POST['redirect'],'loginErr':1})

        if not request.POST['redirect'] == '':
            return redirect(request.POST['redirect'])
        else:
            return redirect('/')

def selectCampus(request):
    sessao = request.session.get('status', 0)

    if sessao:
        campi = Campus.objects.all()
        return render(request,'painelSelecCampus.html',{'campi':campi})
    else:
        return redirect('/login?'+urlencode({'redirect':'/painelCampus'}))

def showPainelCampus(request,campus):
    sessao = request.session.get('status', 0)

    if sessao:
        return painelCampus.painel(request,campus)
    else:
        return redirect('/login?'+urlencode({'redirect':'/painelCampus/'+campus}))

def indicesDeMerito(request):
    sessao = request.session.get('status', 0)

    if sessao:
        return render(request,'indicesDeMerito.html')
    else:
        return redirect('/login?'+urlencode({'redirect':'/indicesDeMerito'}))
