from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import urlencode
from . import painelCampus
from . import envios
from .models import Campus
from .models import FaixasIP
from django.views.decorators.csrf import csrf_exempt
import datetime
import ipaddress
# Create your views here.

def index(request):
    return redirect('/painelCampus')
    #return render(request,'index.html')

@csrf_exempt
def login(request):
    if request.method == 'GET':
        redir = ''
        if 'redirect' in request.GET:
            redir = request.GET['redirect']

        #Pula exigencia de senha se o acesso vier da rede da UT.
        faixas = FaixasIP.objects.all()
        ip = ipaddress.ip_address(request.META['REMOTE_ADDR'])
        lib = 0
        for faixa in faixas:
            if ip in ipaddress.ip_network(faixa.pref):
                lib = 1

        if lib:
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
    campi = Campus.objects.all()
    return render(request,'painelSelecCampus.html',{'campi':campi})

def showPainelCampus(request,campus):
    return painelCampus.painel(request,campus)

def selectCampusOpt(request):
    sessao = request.session.get('status', 0)

    if sessao:
        campi = Campus.objects.all()
        datamax = datetime.datetime.now() - datetime.timedelta(days=1)
        datamaxtext = datamax.strftime("%Y-%m-%d")
        return render(request,'selecCampusOpt.html',{'campi':campi,'datamax':datamaxtext})
    else:
        return redirect('/login?'+urlencode({'redirect':'/painelCampus/opcoes/'}))

def indicesDeMerito(request):
    sessao = request.session.get('status', 0)

    if sessao:
        return render(request,'indicesDeMerito.html')
    else:
        return redirect('/login?'+urlencode({'redirect':'/indicesDeMerito'}))

def listaEnvios(request):
    sessao = request.session.get('status', 0)

    if sessao:
        return envios.listaEnvios(request)
    else:
        return redirect('/login?'+urlencode({'redirect':'/envios'}))

@csrf_exempt
def limpaAlarmes(request):
    sessao = request.session.get('status', 0)

    if sessao:
        return envios.limpaAlarmes(request)
    else:
        return redirect('/login?'+urlencode({'redirect':'/envios'}))
