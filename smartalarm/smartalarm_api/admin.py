from django.contrib import admin
from .models import Tracker, TrackerStat, TrackerEvent, Asset, Trip, TripStat


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_number', 'tracker')


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity', 'imei')
    search_fields = ['name', 'imei']


@admin.register(TrackerStat)
class TrackerStatsAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'lat', 'lon', 'alt', 'satellites', 'speed', 'bat_level', 'is_charging',
                    'car_voltage', 'update_time')
    list_filter = (
        ('satellites', admin.AllValuesFieldListFilter),
        ('bat_level', admin.AllValuesFieldListFilter),
        ('is_charging', admin.BooleanFieldListFilter),
    )

    search_fields = ['tracker', 'event_type']
    ordering = ("-update_time",)


@admin.register(TrackerEvent)
class TrackerEventsAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'event_type', 'update_time')
    list_filter = (
        ('event_type', admin.AllValuesFieldListFilter),
    )
    search_fields = ['tracker', 'event_type']
    ordering = ("-update_time",)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('tracker','update_time', 'address_start', 'address_end')

@admin.register(TripStat)
class TripStatAdmin(admin.ModelAdmin):
    list_display = ('trip', 'stats', 'created')
