from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import invConfig

urlpatterns = [
    path('',views.index),
    path('login',views.login),
    path('painelCampus/',views.selectCampus),
    path('painelCampus/opcoes/',views.selectCampusOpt),
    path('painelCampus/<str:campus>/',views.showPainelCampus),
    path('indicesDeMerito',views.indicesDeMerito),
    path('envios/', views.listaEnvios),
    path('envios/limpaAlarmes',views.limpaAlarmes),
    path('invConfig/api/getValues',invConfig.getInvConfig),
    path('invConfig/api/update',invConfig.updateInvConfig)
]
