from rest_framework import serializers
from . import models

class FRBEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FRBEvent
        fields = '__all__'