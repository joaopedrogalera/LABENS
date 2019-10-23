from django.shortcuts import render
from datetime import datetime
import csv
import os.path
from calendar import monthrange
from .models import Campus
from django.http import HttpResponse

def ProcessaCSV(arquivo):
    retorno = {'Geracao':[],'Inst': 0, 'Erro': 0}

    if os.path.isfile(arquivo):
        csvFile = open(arquivo, newline='')
        reader = csv.reader(csvFile, delimiter='	')

        status = 1

        for row in reader:
            retorno['Inst'] = row[6]
            status = row[10]

            if retorno['Inst'] == '':
                retorno['Inst'] = 0

            retorno['Geracao'].append(retorno['Inst'])

        if status == '2':
            retorno['Erro'] = 1

        csvFile.close()

    return retorno

def painel(request,campus):
    DropboxPath = '/home/labens/Dropbox/'
    try:
        campus = Campus.objects.get(cod=campus)
    except Campus.DoesNotExist:
        return redirect('/')

    data = datetime.now()

    #Arquivos de geração do dia
    csvInvPrefix = DropboxPath+'Aplicativos/LABENS-scada/leituras/'+data.strftime("%Y")+'/'+data.strftime("%m")+'/inversores/'

    mono1File = csvInvPrefix+'mono/inv-2'+str(campus.id)+'a01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    mono2File = csvInvPrefix+'mono/inv-2'+str(campus.id)+'a02_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli1File = csvInvPrefix+'poli/inv-2'+str(campus.id)+'b01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli2File = csvInvPrefix+'poli/inv-2'+str(campus.id)+'b02_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cdteFile = csvInvPrefix+'cdte/inv-1'+str(campus.id)+'c01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cigsFile = csvInvPrefix+'cigs/inv-1'+str(campus.id)+'d01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'

    mono1 = ProcessaCSV(mono1File)
    mono2 = ProcessaCSV(mono2File)
    poli1 = ProcessaCSV(poli1File)
    poli2 = ProcessaCSV(poli2File)
    cdte = ProcessaCSV(cdteFile)
    cigs = ProcessaCSV(cigsFile)

    context = {'campus':campus,
                'mono1':mono1,
                'mono2':mono2,
                'poli1':poli1,
                'poli2':poli2,
                'cdte':cdte,
                'cigs':cigs}

    return render(request,'painelCampus.html',context)
