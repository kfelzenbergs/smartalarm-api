from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from models import Tracker, TrackerStat, TrackerEvent


class DataGatewayView(APIView):
    def get(self, request, format=None):

        return Response(
            {
                'message': 'Test!'
            },
            status=status.HTTP_200_OK
        )

    def post(self, request, format=None):
        data_received = request.data
        print "received:", data_received

        stats_entry = TrackerStat(
            tracker=Tracker.objects.get(identity=data_received.get('identity')),
            lat=data_received.get('lat'),
            lon=data_received.get('lon'),
            satellites=data_received.get('satelites'),
            bat_level=data_received.get('bat_level'),
            is_charging=data_received.get('is_charging')
        )

        stats_entry.save()

        return Response(
            status=status.HTTP_200_OK
        )