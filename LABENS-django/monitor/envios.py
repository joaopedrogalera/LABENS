import sqlite3
from django.http import HttpResponse
from .models import Campus
from django.shortcuts import render, redirect
import datetime

def listaEnvios(request):
    DBPath = '/home/joaopedro/database.db'

    conn = sqlite3.connect(DBPath)

    cur = conn.cursor()
    curUp = conn.cursor()

    campi = Campus.objects.all()

    leituras = []
    for campus in campi:
        tabelas = []
        for file in cur.execute("SELECT * FROM files WHERE local = :campus",{"campus": campus.cod}):
            curUp.execute("SELECT measure_time, last_update_in_s FROM updates WHERE file_id = :file ORDER BY id DESC LIMIT 1",{"file":file[0]})
            result = curUp.fetchone()
            tabelas.append({"file":file[1]+"_"+file[2]+"_"+file[4]+"_"+str(file[5]).zfill(2),"measure_time":datetime.datetime.strptime(result[0],'%Y-%m-%dT%H:%M:%S'),"last_update":result[1]})

        leituras.append({"campus":campus.nome,"tabelas":tabelas})

    return render(request,"listaEnvios.html",{"leituras":leituras})
