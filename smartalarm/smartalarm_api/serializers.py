from rest_framework import serializers
from models import Tracker, TrackerStat, TrackerEvent, Asset
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
            'update_time'
        ]


class TrackerHistoricStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerStat
        fields = [
            'lat',
            'lon',
        ]
