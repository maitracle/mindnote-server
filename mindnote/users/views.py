from django.contrib.auth import authenticate
from django.db import transaction
from django_rest_framework_mango.mixins import PermissionMixin
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from services.google import GoogleClient
from users.models import User
from users.serializers import UserSerializer, TokenSerializer


class UserViewSet(
    PermissionMixin,
    UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_by_actions = {
        'create': (AllowAny,),
        'tokens': (AllowAny,),
        'my_profile': (IsAuthenticated,),
    }

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        created_user = user_serializer.save()

        created_user.set_password(request.data['password'])
        created_user.save()

        token, created = Token.objects.get_or_create(user=created_user)

        response_data = TokenSerializer({'user': created_user, 'token': token}).data

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def tokens(self, request, *args, **kwargs):
        user = authenticate(username=request.data['email'], password=request.data['password'])

        if user is not None:
            token = Token.objects.get(user=user)

            serializer = TokenSerializer({'user': user, 'token': token})

            return Response(serializer.data)
        else:
            raise AuthenticationFailed()

    @action(detail=False, methods=['get'], url_path='my-profile')
    def my_profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def google(self, request, *args, **kwargs):
        try:
            o_auth_token = request.data['o_auth_token']
        except KeyError as e:
            raise ValidationError(f'{e} is required')

        user, is_created = GoogleClient.instance().get_user_or_create_with_google(o_auth_token)
        token = user.get_token()

        response_data = TokenSerializer({'user': user, 'token': token}).data
        response_status = status.HTTP_201_CREATED if is_created else status.HTTP_200_OK

        return Response(response_data, status=response_status)
