from django_filters.rest_framework import DjangoFilterBackend
from django_rest_framework_mango.mixins import PermissionMixin, QuerysetMixin, SerializerMixin
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin, \
    ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from articles.models import Article, Note, Connection
from articles.serializers import ArticleSerializer, NoteSerializer, RetrieveArticleSerializer, ConnectionSerializer
from commons.mixins import CreateWithRequestUserMixin, MyListMixin


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, views, obj):
        return obj.user.id == request.user.id


class ArticleViewSet(
    QuerysetMixin, PermissionMixin, SerializerMixin,
    CreateWithRequestUserMixin, MyListMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    serializer_class_by_actions = {
        'retrieve': RetrieveArticleSerializer
    }
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
        return queryset.filter(user=self.request.user.id).filter(is_published=False)


class IsArticleOwnerUserOnly(permissions.BasePermission):
    def has_object_permission(self, request, views, obj):
        return obj.article.user == request.user


class NoteViewSet(
    QuerysetMixin, PermissionMixin,
    CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (IsArticleOwnerUserOnly,)
    permission_by_actions = {
        'list': (IsAuthenticated,),
    }
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('article',)

    def list(self, request, *args, **kwargs):
        if 'article' not in request.query_params:
            # Todo(maitracle): 적절한 에러 메시지를 세팅한다.
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


class ConnectionViewSet(
    QuerysetMixin, PermissionMixin,
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = (IsArticleOwnerUserOnly,)
