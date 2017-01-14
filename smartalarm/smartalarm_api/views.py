from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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

        return Response(
            {
                'message': "You POSTed {}".format(data_received)
            },
            status=status.HTTP_200_OK
        )