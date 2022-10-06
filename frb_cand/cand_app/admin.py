from django.contrib import admin

from . import models

admin.site.register(models.FRBEvent)
admin.site.register(models.Position)
