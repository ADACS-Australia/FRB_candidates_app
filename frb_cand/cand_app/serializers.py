from rest_framework import serializers
from . import models


class FRBEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FRBEvent
        fields = '__all__'


class RadioMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RadioMeasurement
        fields = '__all__'