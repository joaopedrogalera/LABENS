from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('api/getValues',views.getInvConfig),
    path('api/update',views.updateInvConfig)
]
