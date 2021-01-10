import json

from assertpy import assert_that
from rest_framework import status
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
        assert_that(response.data['user']['email']).is_equal_to(user_data['email'])
        hashed_password_prefix = 'pbkdf2_sha256$216000$'
        assert_that(response.data['user']['password'].startswith(hashed_password_prefix)).is_true()
        assert_that(response.data['user']['name']).is_equal_to(user_data['name'])
        blank_string = ''
        assert_that(response.data['user']['profile_image_url']).is_equal_to(blank_string)

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
