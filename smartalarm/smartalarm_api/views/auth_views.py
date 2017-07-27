from rest_framework import generics
from smartalarm_api.serializers import (LoginSerializer, UserCreateSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import serializers


class UserProfileView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get (self, request, *args, **kwargs):
        user_data = User.objects.filter(pk=request.user.pk).values('email', 'first_name', 'last_name').first()
        # user_token = Token.objects.filter(user=request.user).values('key').first()
        # user_data['access_token'] = user_token['key']

        return Response(user_data, status=status.HTTP_200_OK)


class UserLoginView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        # Validate login data
        login_serializer = LoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)

        # Check if user credentials are valid
        user = authenticate(
            username=login_serializer.data['username'],
            password=login_serializer.data['password']
        )

        # Return bad request if user can't be authenticated
        if user is None:
            return Response({'detail': 'Email and/or password is incorrect'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate new access token
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        file_id = login_serializer.data.get('file_id', None)

        # Mark user as logged in
        user.last_login = timezone.now()
        user.save()

        # Serialize user data
        user_serializer = UserCreateSerializer(user)
        response = user_serializer.data

        return Response(response, status=status.HTTP_200_OK)