from abc import ABC

from rest_framework.exceptions import ValidationError

from services.exceptions import ExternalRequestTimeoutOrUnreachable
from services.requests import Request
from users.models import User
from django.conf import settings


class GoogleClient(ABC):
    @classmethod
    def instance(cls):
        if settings.TEST:
            return GoogleClientWithTest()

        return GoogleClientWithRequest()

    @classmethod
    def _get_google_account_info(cls, o_auth):
        pass

    @classmethod
    def get_user_or_create_with_google(cls, o_auth):
        google_account_info = cls._get_google_account_info(o_auth)

        user, is_created = User.objects.get_or_create(email=google_account_info['email'])

        if is_created:
            user.name = google_account_info['name']
            user.save()

        return user, is_created


class GoogleClientWithRequest(GoogleClient):
    GOOGLE_GET_EMAIL_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

    @classmethod
    def _get_google_account_info(cls, o_auth):
        request = Request.instance()

        try:
            response = request.get(f'{cls.GOOGLE_GET_EMAIL_URL}?access_token={o_auth}')
            parsed_response = response.json()

            return {
                'email': parsed_response['email'],
                'name': parsed_response['name'],
            }

        except:
            raise ValidationError('Failed to get google account information with o auth token')


class GoogleClientWithTest(GoogleClient):
    mocked_google_account_info = {
        'email': 'mocked_email@google.com',
        'name': 'mocked name',
    }

    valid_google_o_auth_token = 'valid_token'
    invalid_google_o_auth_token = 'invalid_token'

    @classmethod
    def _get_google_account_info(cls, o_auth):
        if o_auth == cls.valid_google_o_auth_token:
            return cls.mocked_google_account_info

        raise ValidationError('Failed to get google account information with o auth token')
