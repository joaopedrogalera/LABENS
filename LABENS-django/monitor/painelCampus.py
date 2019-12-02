from django.shortcuts import render, redirect
import datetime
import csv
import os.path
from calendar import monthrange
from .models import Campus
from . import paths
from django.http import HttpResponse

def ProcessaCSV(arquivo):
    retorno = {'Geracao':[],'Inst': 0, 'Erro': 0}

    data = datetime.datetime.now()
    initialTime = datetime.datetime.strptime(data.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(hours=3)

    if os.path.isfile(arquivo):
        csvFile = open(arquivo, newline='')
        reader = csv.reader((x.replace('\0', '') for x in csvFile), delimiter='	') #As vezes algums linha vem com uns NULL no meio e o sistema trava. O replace e o for tratam isso

        status = 1

        for row in reader:
            entrydate = datetime.datetime.strptime(row[0].split('.')[0],'%Y-%m-%dT%H:%M:%S')
            if entrydate >= initialTime:
                #Os dados corrompidos vem de duas formas, com a linha incompleta ou com o campo vazio. Em abos os casos, repete a entrada anterior
                if len(row)>=11:
                    retorno['Inst'] = row[6]
                    status = row[10]
                else:
                    status = 2

                if retorno['Inst'] == '':
                    retorno['Inst'] = retorno['Geracao'][len(retorno['Geracao'])-1]

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

    radFile = paths.Ftp()+campus.cod.upper()+'_'+StationType+'/TAB_RAD_01.csv'
    metFile = paths.Ftp()+campus.cod.upper()+'_'+StationType+'/TAB_RAD_10.csv'
    cmpFile = paths.Ftp()+campus.cod.upper()+'_'+StationType+'/TAB_COMPLEMENTAR.csv'

    #Leva a data para a meia noite do dia atual para comparar com o tempo dos arquivos do ftp
    initialTime = datetime.datetime.strptime(data.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(hours=3)
    finalTime = initialTime + datetime.timedelta(days=1)

    #Inicializa variaveis que serão renderizadas na página
    irradianciaGraf = {'Global':[],'Inclinado':[]}

    dadosMeteorologicos =[
        {'titulo':'Temperatura Ambiente','valor':'N/D','unidade':'°C'},
        {'titulo':'Umidade Relativa do Ar','valor':'N/D','unidade':'%'},
        {'titulo':'Velocidade do Vento','valor':'N/D','unidade':'m/s'},
    ]

    irradiancia = [
        {'titulo':'Plano Inclinado','valor':'N/D'},
        {'titulo':'Global Horizontal','valor':'N/D'}
    ]

    painelTemp = [
        {'tecnologia':'Monocristalino','temp':'N/D'},
        {'tecnologia':'Policristalino','temp':'N/D'},
        {'tecnologia':'CdTe','temp':'N/D'},
        {'tecnologia':'CIGS','temp':'N/D'}
    ]

    #Adiciona campos extras para estações SONDA
    if campus.estTipo == 0:
        dadosMeteorologicos.append({'titulo':'Direção do Vento','valor':'N/D','unidade':'°'})
        dadosMeteorologicos.append({'titulo':'Pressão Atmosférica','valor':'N/D','unidade':'mbar'})
        dadosMeteorologicos.append({'titulo':'Pluviosidade','valor':'N/D','unidade':'mm'})

        irradiancia.append({'titulo':'Direta Normal','valor':'N/D'})
        irradiancia.append({'titulo':'Difusa','valor':'N/D'})

    #Dados de irradiância
    if os.path.isfile(radFile):
        datRad = open(radFile, newline='')
        reader = csv.reader(datRad, delimiter=',')
        #Pula as primeiras quatro linhas do arquivo
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            #Vê a data da entrada e só pega as do dia
            entrydate = datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S')
            if entrydate >= initialTime and entrydate <= finalTime:
                #As vezes a linha vem com um NAN e trava o gráfico. Tratando isto
                if row[6] != 'NAN':
                    irradianciaGraf['Global'].append(row[6])
                else:
                    irradianciaGraf['Global'].append(0)

                if row[10] != 'NAN':
                    irradianciaGraf['Inclinado'].append(row[10])
                else:
                    irradianciaGraf['Inclinado'].append(0)

                irradiancia[0]['valor'] = float(row[10]) #Plano Inclinado
                irradiancia[1]['valor'] = float(row[6]) #Global Horizontal

                #Caso seja SONDA
                if campus.estTipo == 0:
                    irradiancia[2]['valor'] = float(row[18]) #Direta Normal
                    irradiancia[3]['valor'] = float(row[14]) #Difusa

        datRad.close()


    #Dados meteorologicos
    if os.path.isfile(metFile):
        datMet = open(metFile, newline='')
        reader = csv.reader(datMet, delimiter=',')
        #Pula as primeiras quatro linhas do arquivo
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            if campus.estTipo == 0:
                dadosMeteorologicos[0]['valor'] = float(row[14]) #T Ambiente
                dadosMeteorologicos[1]['valor'] = float(row[15]) #Umidade
                dadosMeteorologicos[2]['valor'] = float(row[6]) #V Vento
                dadosMeteorologicos[3]['valor'] = float(row[10]) #Dir Vento
                dadosMeteorologicos[4]['valor'] = float(row[16]) #Pressão
                dadosMeteorologicos[5]['valor'] = float(row[17]) #Pluviosidade
            else:
                dadosMeteorologicos[0]['valor'] = float(row[10]) #T Ambiente
                dadosMeteorologicos[1]['valor'] = float(row[11]) #Umidade
                dadosMeteorologicos[2]['valor'] = float(row[6]) #V Vento


        datMet.close()

    #Dados de temperatura dos paineis
    if os.path.isfile(cmpFile):
        datCmp = open(cmpFile, newline='')
        reader = csv.reader(datCmp, delimiter=',')
        #Pula as primeiras quatro linhas do arquivo
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            painelTemp[0]['temp'] = float(row[6]) #Monocristalino
            painelTemp[1]['temp'] = float(row[10]) #Policristalino
            painelTemp[2]['temp'] = float(row[18]) #CdTe
            painelTemp[3]['temp'] = float(row[14]) #CIGS


        datCmp.close()

    context = {'campus':campus,
                'estTipo': StationType,
                'mono1':mono1,
                'mono2':mono2,
                'poli1':poli1,
                'poli2':poli2,
                'cdte':cdte,
                'cigs':cigs,
                'irradianciaGraf':irradianciaGraf,
                'dadosMeteorologicos':dadosMeteorologicos,
                'irradiancia':irradiancia,
                'painelTemp':painelTemp}

    return render(request,'painelCampus.html',context)
