from django.shortcuts import render
from datetime import datetime
import csv
from calendar import monthrange
from .models import Campus
from django.http import HttpResponse

def painel(request,campus):
    DropboxPath = '/home/labens/Dropbox/'
    try:
        campus = Campus.objects.get(cod=campus)
    except Campus.DoesNotExist:
        return redirect('/')

    data = datetime.now()

    #Arquivos de geração do dia
    csvInvPrefix = DropboxPath+data.strftime("%Y")+'/'+data.strftime("%m")+'/inversores/'

    mono1File = csvInvPrefix+'mono/inv-2'+str(campus.id)+'a01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    mono2File = csvInvPrefix+'mono/inv-2'+str(campus.id)+'a02_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli1File = csvInvPrefix+'poli/inv-2'+str(campus.id)+'b01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli2File = csvInvPrefix+'poli/inv-2'+str(campus.id)+'b02_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cigsFile = csvInvPrefix+'cigs/inv-1'+str(campus.id)+'c01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cdteFile = csvInvPrefix+'cdte/inv-1'+str(campus.id)+'d01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'

    #Arquivos de geração do mês anterior para calcular a produtividade
    if not data.strftime("%m")=='01':
        lastMonthYear = data.strftime("%Y")

        lastMonth = int(data.strftime("%m"))-1
        if lastMonth < 10:
            lastMonth = '0'+str(lastMonth)
        else:
            lastMonth = str(lastMonth)
    else:
        lastMonthYear = str(int(data.strftime("%Y"))-1)
        lastMonth = '12'

    csvInvPrefixOld = DropboxPath+lastMonthYear+'/'+lastMonth+'/inversores/'
    lastMonthDays = monthrange(int(lastMonthYear),int(lastMonth))

    mono1FileOld = csvInvPrefixOld+'mono/inv-2'+str(campus.id)+'a01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    mono2FileOld = csvInvPrefixOld+'mono/inv-2'+str(campus.id)+'a02_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    poli1FileOld = csvInvPrefixOld+'poli/inv-2'+str(campus.id)+'b01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    poli2FileOld = csvInvPrefixOld+'poli/inv-2'+str(campus.id)+'b02_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    cigsFileOld = csvInvPrefixOld+'cigs/inv-1'+str(campus.id)+'c01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    cdteFileOld = csvInvPrefixOld+'cdte/inv-1'+str(campus.id)+'d01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'

    #iniciando valores a serem exibidos na página
    monoGeracao = []
    monoInst = 0
    poliGeracao = []
    poliInst = 0
    cigsGeracao = []
    cigsInst = 0
    cdteGeracao = []
    cdteInst = 0


    context = {'campus':campus,
                'monoGeracao':monoGeracao,
                'monoInst':monoInst,
                'poliGeracao':poliGeracao,
                'poliInst':poliInst,
                'cigsGeracao':cigsGeracao,
                'cigsInst':cigsInst,
                'cdteGeracao':cdteGeracao,
                'cdteInst':cdteInst}

    return render(request,'painel.html',context)
