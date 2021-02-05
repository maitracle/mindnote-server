from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from articles.models import Article, Note, Connection


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


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = (
            'id',
            'article',
            'left_note',
            'right_note',
            'reason',
            'created_at',
            'updated_at',
        )

    def validate(self, attrs):
        if attrs['article'].user != self.context['request'].user:
            raise PermissionDenied(detail='connection can be created at own article')

        if attrs['left_note'] == attrs['right_note']:
            raise ValidationError(detail="notes can't be same")

        if attrs['left_note'].article != attrs['article'] or attrs['right_note'].article != attrs['article']:
            raise ValidationError(detail='notes and article are not matched')

        return attrs


class RetrieveArticleSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True)
    connections = ConnectionSerializer(many=True)

    class Meta:
        model = Article
        fields = (
            'id',
            'user',
            'subject',
            'description',
            'notes',
            'connections',
            'created_at',
            'updated_at',
        )
