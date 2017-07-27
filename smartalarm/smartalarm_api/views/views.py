from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from smartalarm_api.models import Tracker, TrackerStat, TrackerEvent
from smartalarm_api.serializers import TrackerSerializer, TrackerStatSerializer, TrackerHistoricStatSerializer, TrackerEventSerializer
from datetime import datetime, timedelta
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from django.db.models import Q


class TrackersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer


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

    def post(self, request, format=None):
        data_received = request.data
        print "received:", data_received

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
        print "received:", data_received

        events_entry = TrackerEvent(
            tracker=Tracker.objects.get(identity=data_received.get('identity')),
            event_type=data_received.get('event_type'),
        )

        events_entry.save()

        return Response(
            status=status.HTTP_200_OK
        )
