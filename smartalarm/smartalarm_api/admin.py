from django.contrib import admin
from .models import Tracker, TrackerStat, TrackerEvent, Asset, Trip, TripStat, Zone, GlobalStat


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_number', 'tracker')


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity', 'imei', 'tracker_type')

    list_filter = (
        ('tracker_type', admin.AllValuesFieldListFilter),
    )

    search_fields = ['name', 'imei']


@admin.register(TrackerStat)
class TrackerStatsAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'lat', 'lon', 'alt', 'satellites', 'speed', 'bat_level', 'car_running',
                    'car_voltage', 'updated_at')
    list_filter = (
        ('satellites', admin.AllValuesFieldListFilter),
        ('bat_level', admin.AllValuesFieldListFilter),
        ('car_running', admin.BooleanFieldListFilter),
    )

    search_fields = ['tracker__name',]
    ordering = ("-updated_at",)


@admin.register(TrackerEvent)
class TrackerEventsAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'event_type', 'updated_at')
    list_filter = (
        ('event_type', admin.AllValuesFieldListFilter),
    )
    search_fields = ['tracker', 'event_type']
    ordering = ("-updated_at",)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('tracker','updated_at', 'address_start', 'address_end')


@admin.register(TripStat)
class TripStatAdmin(admin.ModelAdmin):
    list_display = ('trip', 'stats', 'created_at')


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'name', 'zone_type', 'alarm_on', 'alarm_enabled', 'created_at', 'updated_at')
    list_filter = (
        ('zone_type', admin.AllValuesFieldListFilter),
        ('alarm_on', admin.AllValuesFieldListFilter),
        ('alarm_enabled', admin.AllValuesFieldListFilter),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GlobalStat)
class GlobalStatAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'distance_traveled', 'count_zero_satellites', 'updated_at')
