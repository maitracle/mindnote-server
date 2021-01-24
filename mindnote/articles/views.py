from django_rest_framework_mango.mixins import PermissionMixin, QuerysetMixin
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from articles.models import Article
from articles.serializers import ArticleSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, views, obj):
        return obj.user.id == request.user.id


class ArticleViewSet(
    QuerysetMixin, PermissionMixin,
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsOwner,)
    permission_by_actions = {
        'create': (IsAuthenticated,),
        'my_list': (IsAuthenticated,),
    }

    def create(self, request, *args, **kwargs):
        data = {
            **request.data,
            'user': request.user.id,
        }
        article_serializer = self.get_serializer(data=data)
        article_serializer.is_valid(raise_exception=True)
        article_serializer.save()

        return Response(article_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-list')
    def my_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def my_list_queryset(self, queryset):
        return queryset.filter(user=self.request.user.id)
