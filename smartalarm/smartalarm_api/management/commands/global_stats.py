from django.core.management.base import BaseCommand
from smartalarm_api.models import (Tracker, TrackerStat, GlobalStat)
from smartalarm_api.aux_functions import calc_distance_from_coords, haversine

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        UPDATE_TIME_MAX = 120

        trackers = Tracker.objects.all()

        for tracker in trackers:
            print "calculating for tracker:", tracker.name
            distance_traveled = 0
            count_zero_satellites = 0
            update_time = 0
            
            gl_s = GlobalStat.objects.filter(tracker=tracker).first()

            if gl_s is not None:
                distance_traveled = gl_s.distance_traveled
                count_zero_satellites = gl_s.count_zero_satellites
                update_time = gl_s.update_time
            else:
                gl_s = GlobalStat(tracker=tracker)

            # get recent tracker stats
            if update_time == 0:
                tracker_stats = TrackerStat.objects.filter(
                    tracker=tracker
                ).order_by('update_time')
            else:
                tracker_stats = TrackerStat.objects.filter(
                    tracker=tracker,
                    update_time__gt=update_time
                ).order_by('update_time')

            distance1 = 0
            distance2 = 0
            # calculate two coordinate distance only for continuous legit possitions
            for i in range(0, len(tracker_stats)-1):
                if tracker_stats[i+1].satellites == 0 or (i == 0 and tracker_stats[i].satellites == 0):
                    count_zero_satellites +=1

                time_between_stat_updates = tracker_stats[i+1].update_time - tracker_stats[i].update_time
                if (
                    # if Owl
                    (tracker.tracker_type == Tracker.TYPE_OWL and 
                    tracker_stats[i].satellites > 0 and 
                    tracker_stats[i+1].satellites > 0) 
                    or
                    # if not Owl 
                    tracker.tracker_type is not Tracker.TYPE_OWL
                    ) and tracker_stats[i].speed > 0 and tracker_stats[i+1].speed > 0 and time_between_stat_updates.seconds < UPDATE_TIME_MAX:                    
                    
                    coords = [
                        (
                            (tracker_stats[i].lat, tracker_stats[i].lon),
                            (tracker_stats[i+1].lat, tracker_stats[i+1].lon),
                        )
                    ]

                    distance1 += haversine(coords)
                    distance2 += calc_distance_from_coords(coords)
                else:
                    pass
            
            gl_s.distance_traveled = round((distance_traveled + distance2), 2)
            gl_s.count_zero_satellites = count_zero_satellites
            gl_s.save()

            print "distance traveled before:", distance_traveled
            print "distance1 for tracker", tracker.name, "is ", distance1
            print "distance2 for tracker", tracker.name, "is ", distance2
