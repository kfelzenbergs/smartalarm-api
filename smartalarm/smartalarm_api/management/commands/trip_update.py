from django.core.management.base import BaseCommand
from smartalarm_api.models import (Trip, TripStat)

class Command(BaseCommand):
    def handle(self, *args, **options):

        def position_has_changed(stats):
            diff = 0.001
            lat_diff = 0
            lon_diff = 0
            # alt_diff = 0

            for i in range(0, len(stats)-1):
                lat_diff += abs(stats[i].stats.lat - stats[i+1].stats.lat)
                lon_diff += abs(stats[i].stats.lon - stats[i+1].stats.lon)
                # alt_diff += abs(stats[i].stats.alt - stats[i+1].stats.alt)
    
            if lat_diff > diff or lon_diff > diff:
                return True
            else:
                return False

        ongoing_trips = Trip.objects.filter(
            finished=False,
        ).order_by('-update_time')

        for trip in ongoing_trips:
            # get recent trip stats
            trip_stats = TripStat.objects.filter(
                trip=trip).order_by('-created')[:5]
            
            # check if last n positions have changed
            if not position_has_changed(trip_stats):
                trip.finished = True
                trip.save()
