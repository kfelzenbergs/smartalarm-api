from rest_framework import serializers
from models import TrackerStat, TrackerEvent


class TrackerStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
            'alt',
            'satellites',
            'speed',
            'bat_level',
            'is_charging',
            'update_time'
        ]


class TrackerEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerEvent
        fields = [
            'event_type',
            'update_time'
        ]


class TrackeHistoricrStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
        ]
