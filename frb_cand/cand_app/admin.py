from django.contrib import admin

from . import models

admin.site.register(models.FRBEvent)
admin.site.register(models.Position)
admin.site.register(models.EventRating)
admin.site.register(models.SlackUser)
