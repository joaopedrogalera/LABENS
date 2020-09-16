from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import urlencode
from . import painelCampus
from . import envios
from .models import Campus
from django.views.decorators.csrf import csrf_exempt
import datetime
import psycopg2
import bcrypt
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

        return render(request,'login.html',{'redirect':redir,'loginErr':0})
    else:
        if not 'redirect' in request.POST or not 'user' in request.POST or request.POST['user'] == '' or not 'passwd' in request.POST or request.POST['passwd'] == '':
            return redirect('/login')

        dbcon = psycopg2.connect(host='',user='',password='',database='')
        cur = dbcon.cursor()
        cur.execute("SELECT password FROM usuarios, roles WHERE usuarios.id_grupo = roles.id AND roles.name IN ('admin','manager') AND usuarios.ativo = 't' AND usuarios.id_login_cpf = %s;",(request.POST['user'],))
        passwd = cur.fetchone()

        if passwd == None:
            return render(request,'login.html',{'redirect':request.POST['redirect'],'loginErr':1})

        if bcrypt.checkpw(request.POST['passwd'].encode('utf-8'),passwd[0].encode('utf-8')):
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
