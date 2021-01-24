from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from articles.models import Article, Note


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'id',
            'user',
            'subject',
            'description',
            'created_at',
            'updated_at',
        )


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = (
            'id',
            'article',
            'contents',
            'created_at',
            'updated_at',
        )

    def validate(self, attrs):
        if 'article' in attrs:
            if attrs['article'].user != self.context['request'].user:
                raise PermissionDenied(detail='note can be created at own article')

        return attrs
