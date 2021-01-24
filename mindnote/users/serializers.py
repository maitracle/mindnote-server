from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'name',
            'profile_image_url',
            'created_at',
            'updated_at',
        )


class TokenSerializer(serializers.Serializer):
    user = UserSerializer()
    token = serializers.CharField()
