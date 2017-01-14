from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from models import TrackerStat


class TrackerStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
            'satellites',
            'bat_level',
            'is_charging'
        ]