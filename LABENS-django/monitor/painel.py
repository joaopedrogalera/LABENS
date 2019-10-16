from django.shortcuts import render
from datetime import datetime
import csv
import os.path
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
    mono = {'Geracao':[],'Inst': 0, 'Erro': 0}
    poli = {'Geracao':[],'Inst': 0, 'Erro': 0}
    cigs = {'Geracao':[],'Inst': 0, 'Erro': 0}
    cdte = {'Geracao':[],'Inst': 0, 'Erro': 0}

    #Mono
    if os.path.isfile(mono1File) and os.path.isfile(mono2File):
        mono1csv = open(mono1File, newline='')
        mono2csv = open(mono2File, newline='')
        mono1reader = csv.reader(mono1csv, delimiter='	')
        mono2reader = csv.reader(mono2csv, delimiter='	')

        mono1finished = 0
        mono2finished = 0

        mono1pot = 0
        mono2pot = 0

        mono1status = 1
        mono2status = 1

        while not mono1finished or not mono2finished:
            if not mono1finished:
                try:
                    mono1row = next(mono1reader)
                    mono1pot = mono1row[6]
                    mono1status = mono1row[10]
                except:
                    mono1finished = 1

            if not mono2finished:
                try:
                    mono2row = next(mono2reader)
                    mono2pot = mono2row[6]
                    mono2status = mono2row[10]
                except:
                    mono2finished = 1

            if mono1pot == '':
                mono1pot = 0

            if mono2pot == '':
                mono2pot = 0

            mono['Inst'] = int(mono1pot) + int(mono2pot)
            mono['Geracao'].append(mono['Inst'])

        if mono1status == '2' or mono2status == '2':
            mono['Erro'] = 1

        mono1csv.close()
        mono2csv.close()

    #Poli
    if os.path.isfile(poli1File) and os.path.isfile(poli2File):
        poli1csv = open(poli1File, newline='')
        poli2csv = open(poli2File, newline='')
        poli1reader = csv.reader(poli1csv, delimiter='	')
        poli2reader = csv.reader(poli2csv, delimiter='	')

        poli1finished = 0
        poli2finished = 0

        poli1pot = 0
        poli2pot = 0

        poli1status = 1
        poli2status = 1

        while not poli1finished or not poli2finished:
            if not poli1finished:
                try:
                    poli1row = next(poli1reader)
                    poli1pot = poli1row[6]
                    poli1status = poli1row[10]
                except:
                    poli1finished = 1

            if not poli2finished:
                try:
                    poli2row = next(poli2reader)
                    poli2pot = poli2row[6]
                    poli2status = poli2row[10]
                except:
                    poli2finished = 1

            if poli1pot == '':
                poli1pot = 0

            if poli2pot == '':
                poli2pot = 0

            poli['Inst'] = int(poli1pot) + int(poli2pot)
            poli['Geracao'].append(poli['Inst'])

        if poli1status == '2' or poli2status == '2':
            poli['Erro'] = 1

        poli1csv.close()
        poli2csv.close()

    context = {'campus':campus,
                'mono':mono,
                'poli':poli,
                'cigs':cigs,
                'cdte':cdte}

    return render(request,'painel.html',context)
