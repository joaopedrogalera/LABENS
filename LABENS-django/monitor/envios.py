import sqlite3
from django.http import HttpResponse
from .models import Campus
from django.shortcuts import render, redirect
import datetime
from . import paths

def formatNoUpdateTime(no_update_time):
    no_update_time_text = ''
    error = 0

    if no_update_time < 60:
        no_update_time_text = str(no_update_time)+'s'
    else:
        no_update_time_s = no_update_time%60
        no_update_time = no_update_time - no_update_time_s
        no_update_time = int(no_update_time/60)

        if no_update_time < 60:
            no_update_time_text = str(no_update_time)+'m '+str(no_update_time_s)+'s'
        else:
            no_update_time_m = no_update_time%60
            no_update_time = no_update_time - no_update_time_m
            no_update_time_text = str(int(no_update_time/60))+'h '+str(no_update_time_m)+'m '+str(no_update_time_s)+'s'
            error = 1

    return {'text':no_update_time_text,'error':error}

def listaEnvios(request):
    DBPath = paths.EnviosDB+'database.db'

    time = datetime.datetime.utcnow()
    conn = sqlite3.connect(DBPath)

    cur = conn.cursor()
    curUp = conn.cursor()

    campi = Campus.objects.all()

    leituras = []
    alarme = 0

    for campus in campi:
        tabelas = []
        for file in cur.execute("SELECT * FROM files WHERE local = :campus",{"campus": campus.cod.upper()}):
            curUp.execute("SELECT measure_time, last_update_in_s FROM updates WHERE file_id = :file ORDER BY id DESC LIMIT 1",{"file":file[0]})
            result = curUp.fetchone()

            measure_time = datetime.datetime.strptime(result[0],'%Y-%m-%dT%H:%M:%S')
            no_update_time = formatNoUpdateTime(int((time-measure_time).total_seconds() + result[1]))

            tabelas.append({"file":file[1]+"-"+file[2],"last_update":measure_time - datetime.timedelta(seconds=result[1]),"no_update_time":no_update_time})

            if file[3] == -2:
                alarme = 1

        leituras.append({"campus":campus.nome,"tabelas":tabelas})

    return render(request,"listaEnvios.html",{"leituras":leituras,"alarme":alarme})

def limpaAlarmes(request):

    if request.method == 'GET':
        return redirect('/envios/')

    if not 'confirm' in request.POST.keys() or not request.POST['confirm'] == '1':
        alert = '''<script>
                    alert("Favor marcar caixa de confirmação");
                    window.location.href = "/envios/";
                </script>'''
        return HttpResponse(alert)
    else:
        DBPath = paths.EnviosDB+'database.db'

        conn = sqlite3.connect(DBPath)
        cur = conn.cursor()
        cur.execute("UPDATE files SET status = -1 WHERE status = -2")
        conn.commit()
        conn.close()
        return HttpResponse('<script>window.location.href = "/envios/";</script>')
