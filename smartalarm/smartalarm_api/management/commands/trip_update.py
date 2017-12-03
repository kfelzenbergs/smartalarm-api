from django.core.management.base import BaseCommand
from smartalarm_api.models import (Trip, TripStat)
from smartalarm_api.aux_functions import get_address_from_coords
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **options):

        def position_has_changed(stats):
            diff = 0.01
            lat_diff = 0
            lon_diff = 0
            speed_sum = 0

            for i in range(0, len(stats)-1):
                lat_diff += abs(stats[i].stats.lat - stats[i+1].stats.lat)
                lon_diff += abs(stats[i].stats.lon - stats[i+1].stats.lon)
                speed_sum += stats[i].stats.speed
            speed_sum += stats[len(stats)-1].stats.speed
    
            if lat_diff > diff or lon_diff > diff or speed_sum > 0:
                return True
            else:
                return False

        ongoing_trips = Trip.objects.filter(
            finished=False,
        ).order_by('-updated_at')

        for trip in ongoing_trips:
            # get recent trip stats
            trip_stats = TripStat.objects.filter(
                trip=trip).order_by('-created_at')
            
            speed_avg = 0
            print trip_stats
            for stat in trip_stats:
                if stat.stats.speed > 0:
                    speed_avg += stat.stats.speed
            
            trip.speed_avg = speed_avg
            trip.save()
            
            trip_stats = trip_stats[:3]
            # check if last n positions have changed
            if not position_has_changed(trip_stats):
                trip.address_end = get_address_from_coords(
                    trip_stats[len(trip_stats)-1].stats.lat, 
                    trip_stats[len(trip_stats)-1].stats.lon
                )
                trip.finished = True
                trip.time_end = timezone.now()
                trip.save()
