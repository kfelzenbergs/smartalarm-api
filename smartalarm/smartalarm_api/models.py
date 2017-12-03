from __future__ import unicode_literals

from django.db import models
import uuid


class Tracker(models.Model):
    identity = models.UUIDField(default=uuid.uuid4, editable=False)
    imei = models.CharField(max_length=256, null=True)
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(max_length=500, blank=True)

    TYPE_UNKNOWN = 1
    TYPE_OWL = 2
    TYPE_COBAN = 3

    tracker_types = (
        (TYPE_UNKNOWN, 'Unknown'),
        (TYPE_OWL, 'Owl'),
        (TYPE_COBAN, 'Coban'),
    )
    tracker_type = models.IntegerField(default=TYPE_UNKNOWN, choices=tracker_types)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class Asset(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_asset')
    name = models.CharField(max_length=256, null=False)
    reg_number = models.CharField(max_length=256, null=False)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TrackerStat(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_stats')
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)
    alt = models.FloatField(default=0)
    satellites = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    bat_level = models.IntegerField(default=0)
    car_running = models.BooleanField(default=False)
    car_voltage = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TrackerEvent(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_events')

    event_choices = (
        ('angle_changed', 'Angel changed'),
        ('position_changed', 'Position changed'),
        ('main_power_disconnected', 'Main power disconnected'),
        ('main_power_connected', 'Main power connected'),
        ('device_armed', 'Device armed'),
        ('device_disarmed', 'Device disarmed'),
        ('trip_started', 'Trip started'),
        ('trip_finished', 'Trip finished'),
        ('ignition_on', 'Ignition on'),
        ('ignition_off', 'Ignition off'),
    )

    event_type = models.CharField(max_length=100, default='unknown', choices=event_choices)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Trip(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_trips')
    finished = models.BooleanField(default=False)
    address_start = models.CharField(max_length=250, default='unknown', null=True, blank=True)
    address_end = models.CharField(max_length=250, default='unknown', null=True, blank=True)
    time_start = models.DateTimeField(auto_now=True)
    time_end = models.DateTimeField(null=True, blank=True)
    speed_avg = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TripStat(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='tripstat_trips')
    stats = models.ForeignKey(TrackerStat, on_delete=models.CASCADE, related_name='tripstat_stats')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Zone(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_zones')
    name = models.CharField(max_length=256, null=False)
    
    ZONE_CIRCLE = 1
    ZONE_RECTANGLE = 2
    ZONE_POLYGON = 3

    zone_choices = (
        (ZONE_CIRCLE, 'Circle'),
        (ZONE_RECTANGLE, 'Rectangle'),
        (ZONE_POLYGON, 'Polygon'),
    )

    zone_type = models.IntegerField(choices=zone_choices, null=True, blank=True)
    bounds = models.CharField(max_length=1000, null=True, blank=True)

    ALARM_ZONE_EXIT = 1
    ALARM_ZONE_ENTER = 2

    alarm_choices = (
        (ALARM_ZONE_EXIT, 'Zone exit'),
        (ALARM_ZONE_ENTER, 'Zone enter')
    )

    alarm_on = models.IntegerField(choices=alarm_choices, null=True, blank=True)
    alarm_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GlobalStat(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_globals')
    distance_traveled = models.FloatField(default=0)
    count_zero_satellites = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
