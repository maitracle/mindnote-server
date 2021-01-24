from rest_framework import serializers

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'id',
            'user',
            'subject',
            'description',
        )


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'id',
            'article',
            'contents',
        )

    def validate(self, attrs):
        print('validate')
        pass
