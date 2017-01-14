from __future__ import unicode_literals

from django.db import models
import uuid


class Tracker(models.Model):
    identity = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, null=False, primary_key=True, unique=True)
    description = models.TextField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name


class TrackerStat(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_stats')
    update_time = models.DateTimeField(auto_now=True)
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)
    satellites = models.IntegerField(default=0)
    bat_level = models.IntegerField(default=0)
    is_charging = models.BooleanField(default=False)


class TrackerEvent(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, related_name='tracker_events')

    event_choices = (
        ('angle_changed', 'Angel changed'),
        ('position_changed', 'Position changed'),
        ('main_power_disconnected', 'Main power disconnected'),
        ('main_power_connected', 'Main power connected'),
    )

    event_type = models.CharField(max_length=100, default='unknown', choices=event_choices)
    update_time = models.DateTimeField(auto_now=True)
