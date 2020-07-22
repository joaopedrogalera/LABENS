from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Campus)
admin.site.register(models.FaixasIP)
admin.site.register(models.InvConfig)
admin.site.register(models.InvConfigTokens)
