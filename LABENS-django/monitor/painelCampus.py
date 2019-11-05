from django.shortcuts import render
import datetime
import csv
import os.path
from calendar import monthrange
from .models import Campus
from . import paths
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
    try:
        campus = Campus.objects.get(cod=campus)
    except Campus.DoesNotExist:
        return redirect('/')

    data = datetime.datetime.now()

    #Arquivos de geração do dia
    csvInvPrefix = paths.Dropbox()+'Aplicativos/LABENS-scada/leituras/'+data.strftime("%Y")+'/'+data.strftime("%m")+'/inversores/'

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
    StationTypes = ['SONDA','EPE']
    StationType = StationTypes[campus.estTipo]

    ambFile = paths.Ftp()+campus.cod.upper()+'_'+StationType+'/TAB_SCADA.DAT'
    pluvFile = paths.Ftp()+campus.cod.upper()+'_'+StationType+'/TAB_RAD_10.DAT'

    #Leva a data para a meia noite do dia atual para comparar com o tempo dos arquivos do ftp
    initialTime = datetime.datetime.strptime(data.strftime('%Y%m%d'),'%Y%m%d')
    finalTime = initialTime + datetime.timedelta(days=1)

    #Inicializa variaveis que serão renderizadas na página
    irradianciaGraf = {'Global':[],'Inclinado':[]}

    dadosMeterologicos =[
        {'titulo':'Temperatura Ambiente','valor':'N/D','unidade':'°C'},
        {'titulo':'Umidade Relativa do Ar','valor':'N/D','unidade':'%'},
        {'titulo':'Velocidade do Vento','valor':'N/D','unidade':'m/s'},
    ]

    irradiancia = [
        {'titulo':'Plano Inclinado','valor':'N/D'},
        {'titulo':'Global Horizontal','valor':'N/D'}
    ]

    #Adiciona campos extras para estações SONDA
    if campus.estTipo == 0:
        dadosMeterologicos.append({'titulo':'Direção do Vento','valor':'N/D','unidade':'°'})
        dadosMeterologicos.append({'titulo':'Pressão Atmosférica','valor':'N/D','unidade':'mbar'})
        dadosMeterologicos.append({'titulo':'Pluviosidade','valor':'N/D','unidade':'mm'})

        irradiancia.append({'titulo':'Direta Normal','valor':'N/D'})
        irradiancia.append({'titulo':'Difusa','valor':'N/D'})

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
                    irradianciaGraf['Global'].append(row[7])
                    irradianciaGraf['Inclinado'].append(row[9])

                    dadosMeterologicos[0]['valor'] = float(row[14]) #T Ambiente
                    dadosMeterologicos[1]['valor'] = float(row[15]) #Umidade
                    dadosMeterologicos[2]['valor'] = float(row[20]) #V Vento
                    dadosMeterologicos[3]['valor'] = float(row[21]) #Dir Vento
                    dadosMeterologicos[4]['valor'] = float(row[13]) #Pressão

                    irradiancia[0]['valor'] = float(row[9]) #Plano Inclinado
                    irradiancia[1]['valor'] = float(row[7]) #Global Horizontal
                    irradiancia[2]['valor'] = float(row[10]) #Direta Normal
                    irradiancia[3]['valor'] = float(row[8]) #Difusa

                else:
                    irradianciaGraf['Global'].append(row[4])
                    irradianciaGraf['Inclinado'].append(row[5])

                    dadosMeterologicos[0]['valor'] = float(row[6]) #T Ambiente
                    dadosMeterologicos[1]['valor'] = float(row[7]) #Umidade
                    dadosMeterologicos[2]['valor'] = float(row[8]) #V Vento

                    irradiancia[0]['valor'] = float(row[5]) #Plano Inclinado
                    irradiancia[1]['valor'] = float(row[4]) #Global Horizontal

        datFile.close()

        if os.path.isfile(pluvFile) and campus.estTipo == 0:
            datPluv = open(pluvFile, newline='')
            readerPluv = csv.reader(datPluv, delimiter=',')

            next(readerPluv)
            next(readerPluv)
            next(readerPluv)
            next(readerPluv)
            for row in readerPluv:
                dadosMeterologicos[5]['valor'] = float(row[17])

            datPluv.close()

    context = {'campus':campus,
                'estTipo': StationType,
                'mono1':mono1,
                'mono2':mono2,
                'poli1':poli1,
                'poli2':poli2,
                'cdte':cdte,
                'cigs':cigs,
                'irradianciaGraf':irradianciaGraf,
                'dadosMeterologicos':dadosMeterologicos,
                'irradiancia':irradiancia}

    return render(request,'painelCampus.html',context)
