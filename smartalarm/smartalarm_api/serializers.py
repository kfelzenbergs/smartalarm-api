from rest_framework import serializers
from models import Tracker, TrackerStat, TrackerEvent, Asset, Trip, TripStat, Zone
from aux_functions import get_address_from_coords
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import (User,)


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
        )

        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }

    def to_representation(self, instance):
        data = super(UserCreateSerializer, self).to_representation(instance)
        data['access_token'] = str(instance.auth_token)

        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.username = validated_data['username']
        instance.save()

        Token.objects.create(user=instance)

        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = [
            'identity',
            'name',
            'description'
        ]

class TrackerStatMinifiedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
            'alt',
            'satellites',
            'speed',
            'bat_level',
            'car_running',
            'car_voltage',
            'updated_at'
        ]


class TrackerStatSerializer(serializers.ModelSerializer):
    last_known_address = serializers.SerializerMethodField()
    last_time_updated = serializers.SerializerMethodField()
    asset_name = serializers.SerializerMethodField()
    asset_reg_nr = serializers.SerializerMethodField()
    tracker_id = serializers.SerializerMethodField()
    tracker_name = serializers.SerializerMethodField()
    last_trip = serializers.SerializerMethodField()

    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
            'alt',
            'satellites',
            'speed',
            'bat_level',
            'car_running',
            'car_voltage',
            'updated_at',
            'last_known_address',
            'last_trip',
            'last_time_updated',
            'asset_name',
            'asset_reg_nr',
            'tracker_id',
            'tracker_name'
        ]

    @staticmethod
    def get_last_trip(obj):
        trip = Trip.objects.filter(tracker=obj.tracker).order_by('-updated_at').first()

        if trip is not None:
            serializer = TripSerializer(trip)
            return serializer.data
        else:
            return "unknown"

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
    def get_last_time_updated(obj):
        stat = TrackerStat.objects.filter(
                tracker=obj.tracker,
                satellites__gte=3
            ).values_list('updated_at').order_by('-updated_at').first()

        if stat is not None:
            return stat[0].strftime("%Y-%m-%dT%H:%M:%S+0300")
        else: 
            return "unknown"

    @staticmethod
    def get_asset_name(obj):
        asset = Asset.objects.filter(tracker=obj.tracker).first()
        return asset.name

    @staticmethod
    def get_asset_reg_nr(obj):
        asset = Asset.objects.filter(tracker=obj.tracker).first()

        return asset.reg_number


class TrackerEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerEvent
        fields = [
            'event_type',
            'updated_at'
        ]


class TrackerHistoricStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
        ]

class TripSerializer(serializers.ModelSerializer):
    tracker = serializers.StringRelatedField()

    class Meta:
        model = Trip
        fields = [
            'id',
            'tracker',
            'finished',
            'address_start',
            'address_end',
            'updated_at'
        ]

class TripStatSerializer(serializers.ModelSerializer):
    trip = TripSerializer()
    stats = TrackerStatMinifiedSerializer()

    class Meta:
        model = TripStat
        fields = [
            'trip',
            'stats'
        ]

class ZoneSerializer(serializers.ModelSerializer):
    tracker = serializers.StringRelatedField()

    class Meta:
        model = Zone
        fields = [
            'id',
            'tracker',
            'name',
            'zone_type',
            'alarm_on',
            'alarm_enabled',
            'bounds',
            'updated_at'
        ]
