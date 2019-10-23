from django.shortcuts import render
import datetime
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

    data = datetime.datetime.now()

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

    #Dados Ambientais
    FtpPath = '/mnt/ftp/'

    StationTypes = ['SONDA','EPE']
    StationType = StationTypes[campus.estTipo]

    ambFile = FtpPath+campus.cod.upper()+'_'+StationType+'/TAB_SCADA.DAT'

    #Leva a data para a meia noite do dia atual para comparar com o tempo dos arquivos do ftp
    initialTime = datetime.datetime.strptime(data.strftime('%Y%m%d'),'%Y%m%d')
    finalTime = initialTime + datetime.timedelta(days=1)

    irradiancia = {'Global':{'Dia':[],'Inst':0},'Inclinado':{'Dia':[],'Inst':0}}

    if os.path.isfile(ambFile):
        datFile = open(ambFile, newline='')
        reader = csv.reader(datFile, delimiter=',')
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            entrydate = datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S')
            if entrydate >= initialTime and entrydate <= finalTime:
                if campus.estTipo == 0:
                    irradiancia['Global']['Dia'].append(row[7])
                    irradiancia['Inclinado']['Dia'].append(row[8])
                else:
                    irradiancia['Global']['Dia'].append(row[4])
                    irradiancia['Inclinado']['Dia'].append(row[5])

        datFile.close()

    context = {'campus':campus,
                'estTipo': StationType,
                'mono1':mono1,
                'mono2':mono2,
                'poli1':poli1,
                'poli2':poli2,
                'cdte':cdte,
                'cigs':cigs,
                'irradiancia':irradiancia}

    return render(request,'painelCampus.html',context)
