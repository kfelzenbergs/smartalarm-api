from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from smartalarm_api.models import Tracker, TrackerStat, TrackerEvent, Trip, TripStat
from smartalarm_api.serializers import TripStatSerializer, TrackerSerializer, TrackerStatSerializer, TrackerHistoricStatSerializer, TrackerEventSerializer
from datetime import datetime, timedelta
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from django.db.models import Q
from twilio.rest import Client as TwClient
from django.conf import settings

class TrackersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer

class TripStatsView(generics.ListAPIView):
    queryset = TripStat.objects.all().order_by('-created')
    serializer_class = TripStatSerializer

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

        latest_status = TrackerStat.objects.filter(
            tracker=tracker
        ).order_by('-update_time').first()

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
                is_charging=request.GET.get('chrg', None),
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
            trip = None
            latest_trip = Trip.objects.filter(tracker=tracker).order_by('-update_time').first()
      
            # if no trips then create first
            if latest_trip is None:
                trip = Trip(tracker=tracker)
                trip.save()

            # continuous trip
            elif latest_trip is not None and not latest_trip.finished:
                if positionHasChanged(latest_trip, pos):
                    trip = latest_trip

            # trip finished. should new trip start?
            else:
                if positionHasChanged(latest_trip, pos):
                    trip = Trip(tracker=tracker)
                    trip.save()

            # add trip stat entry
            if trip is not None:
                trip_stat_entry = TripStat(
                    trip=trip,
                    stats=stats_entry
                )
                trip_stat_entry.save() 

        def positionHasChanged(trip, pos):
            latest_stat = TripStat.objects.filter(trip=trip).order_by('-created').first()
            
            if latest_stat is None:
                return True
            elif abs(float(latest_stat.stats.lat) - float(pos[0])) > 0.01 or abs(float(latest_stat.stats.lon) != float(pos[1])) > 0.01:
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
                is_charging=data_received.get('is_charging'),
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

        historic_stats = TrackerStat.objects.filter(
            tracker=tracker,
            update_time__range=(filter_from, filter_to),
            satellites__gte=3
        ).order_by('update_time')
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
        ).order_by('-update_time').first()

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
            ).order_by('-update_time').first()

            trip.finished = True
            trip.save()

        return Response(
            status=status.HTTP_200_OK
        )
