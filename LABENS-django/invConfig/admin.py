from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.InvConfig)
admin.site.register(models.InvConfigTokens)
