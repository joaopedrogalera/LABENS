from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',views.index),
    path('painel/',RedirectView.as_view(url='/')),
    path('painel/<str:campus>/',views.showPainel),
]
