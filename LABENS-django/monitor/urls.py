from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',views.index),
    path('painelCampus/',RedirectView.as_view(url='/')),
    path('painelCampus/<str:campus>/',views.showPainelCampus),
]
