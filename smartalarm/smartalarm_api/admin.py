from django.contrib import admin
from .models import Tracker, TrackerStat, TrackerEvent

@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity')
    search_fields = ['name']


@admin.register(TrackerStat)
class TrackerStatsAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'lat', 'lon', 'satellites', 'speed', 'bat_level', 'is_charging', 'update_time')
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
