from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class CreateWithRequestUserMixin:
    def create(self, request, *args, **kwargs):
        data = {
            **request.data,
            'user': request.user.id,
        }
        article_serializer = self.get_serializer(data=data)
        article_serializer.is_valid(raise_exception=True)
        article_serializer.save()

        return Response(article_serializer.data, status=status.HTTP_201_CREATED)


class MyListMixin:
    @action(detail=False, methods=['get'], url_path='my-list')
    def my_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def my_list_queryset(self, queryset):
        return queryset.filter(user=self.request.user.id)