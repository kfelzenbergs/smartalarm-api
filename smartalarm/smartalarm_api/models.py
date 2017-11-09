from __future__ import unicode_literals

from django.db import models
import uuid


class Tracker(models.Model):
    identity = models.UUIDField(default=uuid.uuid4, editable=False)
    imei = models.CharField(max_length=256, null=True)
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name


class Asset(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_asset')
    name = models.CharField(max_length=256, null=False)
    reg_number = models.CharField(max_length=256, null=False)
    phone_number = models.CharField(max_length=50, null=True, blank=True)


class TrackerStat(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_stats')
    update_time = models.DateTimeField(auto_now=True)
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)
    alt = models.FloatField(default=0)
    satellites = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    bat_level = models.IntegerField(default=0)
    is_charging = models.BooleanField(default=False)
    car_voltage = models.FloatField(default=0)


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
    update_time = models.DateTimeField(auto_now=True)


class Trip(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_trips')
    finished = models.BooleanField(default=False)
    update_time = models.DateTimeField(auto_now=True)


class TripStat(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='tripstat_trips')
    stats = models.ForeignKey(TrackerStat, on_delete=models.CASCADE, related_name='tripstat_stats')
    created = models.DateTimeField(auto_now=True)
