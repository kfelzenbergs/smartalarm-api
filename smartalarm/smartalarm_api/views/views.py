from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from smartalarm_api.models import Tracker, TrackerStat, TrackerEvent, Trip, TripStat, Zone
from smartalarm_api.serializers import ZoneSerializer, TripSerializer, TripStatSerializer, TrackerSerializer, TrackerStatSerializer, TrackerHistoricStatSerializer, TrackerEventSerializer
from datetime import datetime, timedelta
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from django.db.models import Q
from twilio.rest import Client as TwClient
from django.conf import settings
from smartalarm_api.aux_functions import get_address_from_coords
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db.models import Count

class TrackersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer

class TripsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    
    queryset = Trip.objects.annotate(
        tripstat_count=Count('tripstat_trips')
    ).filter(
        tripstat_count__gte=2
    ).order_by('-updated_at')

    serializer_class = TripSerializer

class TripStatsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TripStatSerializer

    def get_queryset(self):
        trip_id = self.request.query_params.get('trip', None)

        queryset = TripStat.objects.filter(
            trip=Trip.objects.get(pk=trip_id)
        )

        return queryset


class ZonesView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        queryset = Zone.objects.all().order_by('-updated_at')
        serializer = ZoneSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        obj_id = request.GET.get('id', None)
        if obj_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            zone = Zone.objects.get(id=obj_id)
            zone.delete()
        except ObjectDoesNotExist as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, format=None):
        obj_id = request.data.get('id', None)
        if obj_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            zone = Zone.objects.get(id=obj_id)
            zone.alarm_on = request.data.get('alarm_on')
            zone.alarm_enabled = request.data.get('alarm_enabled')
            zone.bounds = json.dumps(request.data.get('bounds'))
            zone.save()

            serializer = ZoneSerializer(zone)
        
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            zone = Zone(
                tracker=Tracker.objects.get(
                    identity=request.data.get('tracker')
                ),
                name=request.data.get('name'),
                zone_type=request.data.get('zone_type'),
                bounds=json.dumps(request.data.get('bounds')),
                alarm_on=request.data.get('alarm_on'),
                alarm_enabled=request.data.get('alarm_enabled')
            )
            zone.save()
            serializer = ZoneSerializer(zone)                       

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print e

            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

class CallsCallbackView(APIView):

    def post(self, request, format=None):
        data_received = request.data
        print "received:", data_received

        callStatus = data_received['CallStatus']
        callSid = data_received['CallSid']

        if callStatus == 'answered' or callStatus == 'in-progress':
            print "attempting to terminate call"

            client = TwClient(getattr(settings, "TW_ACCOUNT_SID", None), getattr(settings, "TW_AUTH_TOKEN", None))

            call = client.calls(callSid) \
                .update(status="completed")

            print(call.direction)

        return Response(
            status=status.HTTP_200_OK
        )


class StatsGatewayView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return []

    def get(self, request, format=None):

        identity = request.GET.get('tracker', None)

        if identity is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tracker = Tracker.objects.get(identity=identity)

        satellites_min = 0
        if tracker.tracker_type == Tracker.TYPE_OWL:
            satellites_min = 3

        latest_status = TrackerStat.objects.filter(
            tracker=tracker,
            satellites__gte=satellites_min
        ).order_by('-updated_at').first()

        serializer = TrackerStatSerializer(latest_status, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put (self, request, format=None):

        try:
            stats_entry = TrackerStat(
                tracker=Tracker.objects.get(
                    Q(identity=request.GET.get('identity', None)) | Q(imei=request.GET.get('imei', None))
                ),
                lat=request.GET.get('lat', None),
                lon=request.GET.get('lon', None),
                alt=request.GET.get('alt', None),
                speed=request.GET.get('speed', None),
                satellites=request.GET.get('sat', None),
                bat_level=request.GET.get('bat', None),
                car_running=request.GET.get('chrg', None),
                car_voltage=request.GET.get('volt', None)
            )

            stats_entry.save()

            return Response(
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print e

            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )


    def post(self, request, format=None):
        data_received = request.data

        def getTrip(tracker, pos):
            new_trip = False
            trip = None
            latest_trip = Trip.objects.filter(tracker=tracker).order_by('-updated_at').first()
      
            # if no trips then create first
            if latest_trip is None:
                trip = Trip(tracker=tracker)
                trip.save()
                new_trip = True

            # continuous trip
            elif latest_trip is not None and not latest_trip.finished:
                if positionHasChanged(latest_trip, pos):
                    trip = latest_trip

            # trip finished. should new trip start?
            else:
                if positionHasChanged(latest_trip, pos):
                    trip = Trip(tracker=tracker)
                    trip.save()
                    new_trip = True

            # add trip stat entry
            if trip is not None:
                trip_stat_entry = TripStat(
                    trip=trip,
                    stats=stats_entry
                )
                trip_stat_entry.save() 

                if new_trip:
                    if latest_trip is not None:
                        trip.address_start = latest_trip.address_end
                    else:
                        trip.address_start = get_address_from_coords(
                            trip_stat_entry.stats.lat, 
                            trip_stat_entry.stats.lon
                        )
                    trip.save()

        def positionHasChanged(trip, pos):
            latest_stat = TripStat.objects.filter(trip=trip).order_by('-created_at').first()
            
            if latest_stat is None:
                return True
            elif abs(float(latest_stat.stats.lat) - float(pos[0])) > 0.001 or abs(float(latest_stat.stats.lon) - float(pos[1])) > 0.001:
                return True
            else:
                return False
        
        try:
            stats_entry = TrackerStat(
                tracker=Tracker.objects.get(
                    Q(identity=data_received.get('identity', None)) | Q(imei=data_received.get('imei', None))
                ),
                lat=data_received.get('lat'),
                lon=data_received.get('lon'),
                alt=data_received.get('alt'),
                speed=data_received.get('speed'),
                satellites=data_received.get('satelites'),
                bat_level=data_received.get('bat_level'),
                car_running=data_received.get('car_running'),
                car_voltage=data_received.get('car_voltage')
            )

            stats_entry.save()

            getTrip(stats_entry.tracker, (stats_entry.lat, stats_entry.lon))
                       

            return Response(
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print e

            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )


class StatsHistoryGatewayView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        identity = request.GET.get('tracker', None)

        if identity is None or identity == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tracker = Tracker.objects.get(identity=identity)

        filter_from = request.GET.get('from', timezone.now() - timedelta(days=1))
        filter_to = request.GET.get('to', timezone.now())

        if isinstance(filter_from, basestring) and isinstance(filter_to, basestring):
            tz = get_current_timezone()
            filter_from = tz.localize(datetime.strptime(filter_from, '%Y-%m-%d'))
            filter_to = tz.localize(datetime.strptime(filter_to, '%Y-%m-%d')).replace(hour=23, minute=59)

        satellites_min = 0
        if tracker.tracker_type == Tracker.TYPE_OWL:
            satellites_min = 3

        historic_stats = TrackerStat.objects.filter(
            tracker=tracker,
            updated_at__range=(filter_from, filter_to),
            satellites__gte=satellites_min,
            lat__gt=0.0,
            lon__gt=0.0
        ).order_by('updated_at')
        serializer = TrackerHistoricStatSerializer(historic_stats, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EventGatewayView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return []

    def get(self, request, format=None):
        identity = request.GET.get('tracker', None)

        if identity is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tracker = Tracker.objects.get(identity=identity)

        latest_status = TrackerEvent.objects.filter(
            tracker=tracker
        ).order_by('-updated_at').first()

        serializer = TrackerEventSerializer(latest_status, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data_received = request.data

        events_entry = TrackerEvent(
            tracker=Tracker.objects.get(identity=data_received.get('identity')),
            event_type=data_received.get('event_type'),
        )

        events_entry.save()

        if events_entry.event_type == 'ignition_off':
            trip = Trip.objects.filter(
                tracker=events_entry.tracker,
                finished=False
            ).order_by('-updated_at').first()

            trip.finished = True
            trip.save()

        return Response(
            status=status.HTTP_200_OK
        )
