import json

from assertpy import assert_that
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase

from users.models import User


class UserViewSetTestCase(APITestCase):
    def test_create_user(self):
        user_data = {
            'email': 'testuser@test.com',
            'password': 'password123',
            'name': 'username',
        }

        response = self.client.post('/users/', data=json.dumps(user_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
        assert_that('token' in response.data).is_true()

        user = User.objects.get(email=user_data['email'])

        assert_that(response.data['user']['id']).is_equal_to(user.id)
        self._assert_user(response.data['user'], user)
        hashed_password_prefix = 'pbkdf2_sha256$216000$'
        assert_that(response.data['user']['password'].startswith(hashed_password_prefix)).is_true()

    def test_should_not_create(self):
        user_data = {
            'email': 'testuser@test.com',
            'password': '',
            'name': 'username',
        }

        response = self.client.post('/users/', data=json.dumps(user_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=user_data['email'])
        assert_that(user).is_empty()

    def test_should_get_token(self):
        user_data = {
            'email': 'testuser@test.com',
            'password': 'password123',
        }
        user = baker.make('users.User', email=user_data['email'])
        user.set_password(user_data['password'])
        user.save()
        expected_token, _created = Token.objects.get_or_create(user=user)

        response = self.client.post('/users/tokens/', data=json.dumps(user_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.data['token']).is_equal_to(expected_token.key)
        self._assert_user(response.data['user'], user)

    def test_should_not_get_token(self):
        user_data = {
            'email': 'testuser@test.com',
            'password': 'password123',
        }
        user = baker.make('users.User', email=user_data['email'])
        user.set_password(user_data['password'])
        user.save()

        wrong_payload = {
            'email': 'testuser@test.com',
            'password': 'wrong_password',
        }
        response = self.client.post('/users/tokens/', data=json.dumps(wrong_payload), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        assert_that(response.data['detail']).is_equal_to(AuthenticationFailed.default_detail)
        assert_that(hasattr(response.data, 'user')).is_false()

    def test_should_get_my_profile(self):
        user = baker.make('users.User')

        self.client.force_authenticate(user=user)
        response = self.client.post('/users/my-profile/', content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        self._assert_user(response.data, user)

    def test_should_not_get_my_profile(self):
        response = self.client.post('/users/my-profile/', content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        assert_that(hasattr(response.data, 'user')).is_false()

    @staticmethod
    def _assert_user(response_user, expect_user):
        assert_that(response_user['id']).is_equal_to(expect_user.id)
        assert_that(response_user['email']).is_equal_to(expect_user.email)
        assert_that(response_user['name']).is_equal_to(expect_user.name)
        assert_that(response_user['profile_image_url']).is_equal_to(expect_user.profile_image_url)
