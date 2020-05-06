from django.shortcuts import render, redirect
import datetime
import csv
import os.path
from calendar import monthrange
from .models import Campus
from . import paths
from django.http import HttpResponse

def ProcessaCSV(arquivo, data):
    retorno = {'Geracao':[],'Inst': 0, 'Erro': 0, 'Timestamp':''}

    initialTime = datetime.datetime.strptime(data.strftime('%Y%m%d'),'%Y%m%d') + datetime.timedelta(hours=3)

    if os.path.isfile(arquivo):
        csvFile = open(arquivo, newline='')
        reader = csv.reader((x.replace('\0', '') for x in csvFile)) #As vezes algums linha vem com uns NULL no meio e o sistema trava. O replace e o for tratam isso

        status = 1

        try:
            next(reader)
        except:
            retorno['Erro'] = 1
            return retorno

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
                retorno['Timestamp'] = entrydate

        if status == '2':
            retorno['Erro'] = 1

        csvFile.close()

    return retorno

def painel(request,campus):
    if len(campus) > 2:
        if campus[2] == '0':
            estTipo = 0
        elif campus[2] == '1':
            estTipo = 1
        else:
            estTipo = ''
        campus = campus[0] + campus[1]
    else:
        estTipo = ''

    try:
        campus = Campus.objects.get(cod=campus)
    except Campus.DoesNotExist:
        return redirect('/')

    if estTipo == '':
        estTipo = campus.estTipo

    if 'data' in request.GET.keys():
        try:
            data = datetime.datetime.strptime(request.GET['data'],"%Y-%m-%d")
        except:
            data = datetime.datetime.now()
    else:
        data = datetime.datetime.now()

    #Arquivos de geração do dia
    csvPrefix = paths.Ftp()+data.strftime("%Y")+'/'+data.strftime("%m")
    csvInvPrefix = csvPrefix+'/inversores/'

    mono1File = csvInvPrefix+'mono/'+campus.cod.upper()+'-mon1-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    mono2File = csvInvPrefix+'mono/'+campus.cod.upper()+'-mon2-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli1File = csvInvPrefix+'poli/'+campus.cod.upper()+'-pol1-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    poli2File = csvInvPrefix+'poli/'+campus.cod.upper()+'-pol2-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cdteFile = csvInvPrefix+'cdte/'+campus.cod.upper()+'-cdte-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cigsFile = csvInvPrefix+'cigs/'+campus.cod.upper()+'-cigs-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'

    mono1 = ProcessaCSV(mono1File, data)
    mono2 = ProcessaCSV(mono2File, data)
    poli1 = ProcessaCSV(poli1File, data)
    poli2 = ProcessaCSV(poli2File, data)
    cdte = ProcessaCSV(cdteFile, data)
    cigs = ProcessaCSV(cigsFile, data)

    #Dados Ambientais
    StationTypes = ['SONDA','EPE']
    StationType = StationTypes[estTipo]

    csvDatPrefix = csvPrefix+'/dataloggers/'

    radFile = csvDatPrefix+'rad01/'+campus.cod.upper()+'-'+StationType.lower()[0]+StationType.lower()[1]+'01-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    metFile = csvDatPrefix+'rad10/'+campus.cod.upper()+'-'+StationType.lower()[0]+StationType.lower()[1]+'10-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    tmpFile = csvDatPrefix+'temps/'+campus.cod.upper()+'-temp-'+data.strftime("%y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'

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

    ambTimestamp = {'irradiancia':'','meteorologicos':'','paineis':''}

    #Adiciona campos extras para estações SONDA
    if estTipo == 0:
        dadosMeteorologicos.append({'titulo':'Direção do Vento','valor':'N/D','unidade':'°'})
        dadosMeteorologicos.append({'titulo':'Pressão Atmosférica','valor':'N/D','unidade':'mbar'})
        dadosMeteorologicos.append({'titulo':'Pluviosidade do dia','valor':'N/D','unidade':'mm'})

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
            entrydate = datetime.datetime.strptime(row[1],'%Y-%m-%dT%H:%M:%SZ')
            if entrydate >= initialTime and entrydate <= finalTime:
                if estTipo == 0: #Se for SONDA
                    #As vezes a linha vem com um NAN e trava o gráfico. Tratando isto
                    if row[2] != 'NAN':
                        irradianciaGraf['Global'].append(row[2])
                    else:
                        irradianciaGraf['Global'].append(0)

                    if row[22] != 'NAN':
                        irradianciaGraf['Inclinado'].append(row[22])
                    else:
                        irradianciaGraf['Inclinado'].append(0)

                    irradiancia[0]['valor'] = round(float(row[22]),1) #Plano Inclinado
                    irradiancia[1]['valor'] = round(float(row[2]),1) #Global Horizontal
                    irradiancia[2]['valor'] = round(float(row[10]),1) #Direta Normal
                    irradiancia[3]['valor'] = round(float(row[6]),1) #Difusa
                else: #Se for EPE
                    #As vezes a linha vem com um NAN e trava o gráfico. Tratando isto
                    if row[2] != 'NAN':
                        irradianciaGraf['Global'].append(row[2])
                    else:
                        irradianciaGraf['Global'].append(0)

                    if row[6] != 'NAN':
                        irradianciaGraf['Inclinado'].append(row[6])
                    else:
                        irradianciaGraf['Inclinado'].append(0)

                    irradiancia[0]['valor'] = round(float(row[6]),1) #Plano Inclinado
                    irradiancia[1]['valor'] = round(float(row[2]),1) #Global Horizontal

                ambTimestamp['irradiancia'] = entrydate

        datRad.close()


    #Dados meteorologicos
    if os.path.isfile(metFile):
        datMet = open(metFile, newline='')
        reader = csv.reader(datMet, delimiter=',')

        #Inicializa a pluviosidade com 0
        if estTipo == 0:
            dadosMeteorologicos[5]['valor'] = float(0)

        #Pula as primeiras quatro linhas do arquivo
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            #Vê a data da entrada e só pega as do dia
            entrydate = datetime.datetime.strptime(row[1],'%Y-%m-%dT%H:%M:%SZ')
            if entrydate >= initialTime and entrydate <= finalTime:
                if estTipo == 0:
                    dadosMeteorologicos[0]['valor'] = round(float(row[2]),1) #T Ambiente
                    dadosMeteorologicos[1]['valor'] = round(float(row[3]),1) #Umidade
                    dadosMeteorologicos[2]['valor'] = round(float(row[6]),1) #V Vento
                    dadosMeteorologicos[3]['valor'] = round(float(row[7]),1) #Dir Vento
                    dadosMeteorologicos[4]['valor'] = round(float(row[4]),1) #Pressão
                    dadosMeteorologicos[5]['valor'] += float(row[5]) #Pluviosidade
                else:
                    dadosMeteorologicos[0]['valor'] = round(float(row[2]),1) #T Ambiente
                    dadosMeteorologicos[1]['valor'] = round(float(row[3]),1) #Umidade
                    dadosMeteorologicos[2]['valor'] = round(float(row[4]),1) #V Vento

                ambTimestamp['meteorologicos'] = entrydate

            if estTipo == 0:
                dadosMeteorologicos[5]['valor'] = round(dadosMeteorologicos[5]['valor'],1)


        datMet.close()

    #Dados de temperatura dos paineis
    if os.path.isfile(tmpFile):
        datTmp = open(tmpFile, newline='')
        reader = csv.reader(datTmp, delimiter=',')
        #Pula as primeiras quatro linhas do arquivo
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        for row in reader:
            painelTemp[0]['temp'] = round(float(row[2]),1) #Monocristalino
            painelTemp[1]['temp'] = round(float(row[3]),1) #Policristalino
            painelTemp[2]['temp'] = round(float(row[5]),1) #CdTe
            painelTemp[3]['temp'] = round(float(row[4]),1) #CIGS

        ambTimestamp['paineis'] = datetime.datetime.strptime(row[1],'%Y-%m-%dT%H:%M:%SZ')


        datTmp.close()

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
                'painelTemp':painelTemp,
                'ambTimestamp':ambTimestamp}

    return render(request,'painelCampus.html',context)
