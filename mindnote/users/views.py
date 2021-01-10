from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer


class UserViewSet(
    UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        created_user = user_serializer.save()

        created_user.set_password(request.data['password'])
        created_user.save()

        token, created = Token.objects.get_or_create(user=created_user)

        response_data = {
            'token': token.key,
            'user': user_serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
