from django_rest_framework_mango.mixins import PermissionMixin, QuerysetMixin
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin, \
    ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from articles.models import Article, Note
from articles.serializers import ArticleSerializer, NoteSerializer
from commons.mixins import CreateWithRequestUserMixin, MyListMixin


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, views, obj):
        return obj.user.id == request.user.id


class ArticleViewSet(
    QuerysetMixin, PermissionMixin,
    CreateWithRequestUserMixin, MyListMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwner,)
    permission_by_actions = {
        'create': (IsAuthenticated,),
        'my_list': (IsAuthenticated,),
    }

    @action(detail=False, methods=['get'], url_path='my-list')
    def my_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def my_list_queryset(self, queryset):
        return queryset.filter(user=self.request.user.id)


class NoteViewSet(
    QuerysetMixin, PermissionMixin,
    CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (IsOwner,)
    permission_by_actions = {
        'create': (IsAuthenticated,),
        'my_list': (IsAuthenticated,),
    }
