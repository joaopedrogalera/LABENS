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
    cdteFile = csvInvPrefix+'cdte/inv-1'+str(campus.id)+'c01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'
    cigsFile = csvInvPrefix+'cigs/inv-1'+str(campus.id)+'d01_'+data.strftime("%Y")+'-'+data.strftime("%m")+'-'+data.strftime("%d")+'.csv'

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
    cdteFileOld = csvInvPrefixOld+'cdte/inv-1'+str(campus.id)+'c01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'
    cigsFileOld = csvInvPrefixOld+'cigs/inv-1'+str(campus.id)+'d01_'+lastMonthYear+'-'+lastMonth+'-'+str(lastMonthDays[1])+'.csv'

    #iniciando valores a serem exibidos na página
    mono = {'Geracao':[],'Inst': 0, 'Erro': 0}
    poli = {'Geracao':[],'Inst': 0, 'Erro': 0}
    cdte = {'Geracao':[],'Inst': 0, 'Erro': 0}
    cigs = {'Geracao':[],'Inst': 0, 'Erro': 0}

    #Variaveis para calcular energia gerada
    monoEnergy = 0
    poliEnergy = 0
    cdteEnergy = 0
    cigsEnergy = 0

    monoEnergyOld = 0
    poliEnergyOld = 0
    cdteEnergyOld = 0
    cigsEnergyOld = 0

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

        mono1Energy = 0
        mono2Energy = 0

        mono1status = 1
        mono2status = 1

        while not mono1finished or not mono2finished:
            if not mono1finished:
                try:
                    mono1row = next(mono1reader)
                    mono1pot = mono1row[6]
                    mono1status = mono1row[10]
                    if float(mono1row[7]) > mono1Energy:
                        mono1Energy = float(mono1row[7])
                except:
                    mono1finished = 1

            if not mono2finished:
                try:
                    mono2row = next(mono2reader)
                    mono2pot = mono2row[6]
                    mono2status = mono2row[10]
                    if float(mono2row[7]) > mono2Energy:
                        mono2Energy = float(mono2row[7])
                except:
                    mono2finished = 1

            if mono1pot == '':
                mono1pot = 0

            if mono2pot == '':
                mono2pot = 0

            mono['Inst'] = int(mono1pot) + int(mono2pot)
            mono['Geracao'].append(mono['Inst'])

        monoEnergy = float(mono1Energy) + float(mono2Energy)

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

        poli1Energy = 0
        poli2Energy = 0

        poli1status = 1
        poli2status = 1

        while not poli1finished or not poli2finished:
            if not poli1finished:
                try:
                    poli1row = next(poli1reader)
                    poli1pot = poli1row[6]
                    poli1status = poli1row[10]
                    if float(poli1row[7]) > poli1Energy:
                        poli1Energy = float(poli1row[7])
                except:
                    poli1finished = 1

            if not poli2finished:
                try:
                    poli2row = next(poli2reader)
                    poli2pot = poli2row[6]
                    poli2status = poli2row[10]
                    if float(poli2row[7]) > poli2Energy:
                        poli2Energy = float(poli2row[7])
                except:
                    poli2finished = 1

            if poli1pot == '':
                poli1pot = 0

            if poli2pot == '':
                poli2pot = 0

            poli['Inst'] = int(poli1pot) + int(poli2pot)
            poli['Geracao'].append(poli['Inst'])

        poliEnergy = float(poli1Energy) + float(poli2Energy)

        if poli1status == '2' or poli2status == '2':
            poli['Erro'] = 1

        poli1csv.close()
        poli2csv.close()

    #cdte
    if os.path.isfile(cdteFile):
        cdtecsv = open(cdteFile, newline='')
        cdtereader = csv.reader(cdtecsv, delimiter='	')

        cdtestatus = 1

        for cdterow in cdtereader:
            cdte['Inst'] = cdterow[6]
            cdtestatus = cdterow[10]
            if float(cdterow[7]) > cdteEnergy:
                cdteEnergy = float(cdterow[7])

            if cdte['Inst'] == '':
                cdte['Inst'] = 0

            cdte['Geracao'].append(cdte['Inst'])

        if cdtestatus == '2':
            cdte['Erro'] = 1

        cdtecsv.close()

    #cigs
    if os.path.isfile(cigsFile):
        cigscsv = open(cigsFile, newline='')
        cigsreader = csv.reader(cigscsv, delimiter='	')

        cigsstatus = 1

        for cigsrow in cigsreader:
            cigs['Inst'] = cigsrow[6]
            cigsstatus = cigsrow[10]
            if float(cigsrow[7]) > cigsEnergy:
                cigsEnergy = float(cigsrow[7])

            if cigs['Inst'] == '':
                cigs['Inst'] = 0

            cigs['Geracao'].append(cigs['Inst'])

        if cigsstatus == '2':
            cigs['Erro'] = 1

        cigscsv.close()

    #Calcula produtividade
    #Mono
    if os.path.isfile(mono1FileOld) and os.path.isfile(mono1FileOld):
        mono1csvOld = open(mono1FileOld, newline='')
        mono2csvOld = open(mono2FileOld, newline='')
        mono1readerOld = csv.reader(mono1csvOld, delimiter='	')
        mono2readerOld = csv.reader(mono2csvOld, delimiter='	')

        mono1EnergyOld = 0
        mono2EnergyOld = 0

        for mono1rowOld in mono1readerOld:
            if float(mono1rowOld[7]) > mono1EnergyOld:
                mono1EnergyOld = float(mono1rowOld[7])

        for mono2rowOld in mono2readerOld:
            if float(mono2rowOld[7]) > mono2EnergyOld:
                mono2EnergyOld = float(mono2rowOld[7])

        monoEnergyOld = mono1EnergyOld + mono2EnergyOld

        mono1csvOld.close()
        mono2csvOld.close()

    #Poli
    if os.path.isfile(poli1FileOld) and os.path.isfile(poli1FileOld):
        poli1csvOld = open(poli1FileOld, newline='')
        poli2csvOld = open(poli2FileOld, newline='')
        poli1readerOld = csv.reader(poli1csvOld, delimiter='	')
        poli2readerOld = csv.reader(poli2csvOld, delimiter='	')

        poli1EnergyOld = 0
        poli2EnergyOld = 0

        for poli1rowOld in poli1readerOld:
            if float(poli1rowOld[7]) > poli1EnergyOld:
                poli1EnergyOld = float(poli1rowOld[7])

        for poli2rowOld in poli2readerOld:
            if float(poli2rowOld[7]) > poli2EnergyOld:
                poli2EnergyOld = float(poli2rowOld[7])

        poliEnergyOld = poli1EnergyOld + poli2EnergyOld

        poli1csvOld.close()
        poli2csvOld.close()

    #cdte
    if os.path.isfile(cdteFileOld):
        cdtecsvOld = open(cdteFileOld, newline='')
        cdtereaderOld = csv.reader(cdtecsvOld, delimiter='	')

        for cdterowOld in cdtereaderOld:
            if float(cdterowOld[7]) > cdteEnergyOld:
                cdteEnergyOld = float(cdterowOld[7])

        cdtecsvOld.close()

    #cigs
    if os.path.isfile(cigsFileOld):
        cigscsvOld = open(cigsFileOld, newline='')
        cigsreaderOld = csv.reader(cigscsvOld, delimiter='	')

        for cigsrowOld in cigsreaderOld:
            if float(cigsrowOld[7]) > cigsEnergyOld:
                cigsEnergyOld = float(cigsrowOld[7])

        cigscsvOld.close()

    produtividade = {'mono':0,'poli':0,'cdte':0,'cigs':0}

    if monoEnergy > monoEnergyOld:
        produtividade['mono'] = (monoEnergy - monoEnergyOld)*1000/(14*365)

    if poliEnergy > poliEnergyOld:
        produtividade['poli'] = (poliEnergy - poliEnergyOld)*1000/(14*335)

    if cdteEnergy > cdteEnergyOld:
        produtividade['cdte'] = (cdteEnergy - cdteEnergyOld)*1000/(18*85)

    if cigsEnergy > cigsEnergyOld:
        produtividade['cigs'] = (cigsEnergy - cigsEnergyOld)*1000/(12*140)

    context = {'campus':campus,
                'mono':mono,
                'poli':poli,
                'cdte':cdte,
                'cigs':cigs,
                'produtividade':produtividade}

    return render(request,'painel.html',context)
