from rest_framework import serializers
from models import TrackerStat, TrackerEvent, Asset
from aux_functions import get_address_from_coords


class TrackerStatSerializer(serializers.ModelSerializer):
    last_known_address = serializers.SerializerMethodField()
    asset_name = serializers.SerializerMethodField()
    asset_reg_nr = serializers.SerializerMethodField()
    tracker_id = serializers.SerializerMethodField()
    tracker_name = serializers.SerializerMethodField()

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
            'update_time',
            'last_known_address',
            'asset_name',
            'asset_reg_nr',
            'tracker_id',
            'tracker_name'
        ]

    @staticmethod
    def get_tracker_id(obj):
        return obj.tracker.identity

    @staticmethod
    def get_tracker_name(obj):
        return obj.tracker.name

    @staticmethod
    def get_last_known_address(obj):
        return get_address_from_coords(obj.lat, obj.lon)

    @staticmethod
    def get_asset_name(obj):
        asset = Asset.objects.filter(tracker=obj.tracker)[0]

        return asset.name

    @staticmethod
    def get_asset_reg_nr(obj):
        asset = Asset.objects.filter(tracker=obj.tracker)[0]

        return asset.reg_number


class TrackerEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerEvent
        fields = [
            'event_type',
            'update_time'
        ]


class TrackerHistoricStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
        ]
