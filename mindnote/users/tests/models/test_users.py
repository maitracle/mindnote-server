from unittest import TestCase

from assertpy import assert_that
from model_bakery import baker
from rest_framework.authtoken.models import Token


class UserTestCase(TestCase):
    def test_should_get_token(self):
        user = baker.make('users.User')
        expected_token = baker.make('authtoken.Token', user=user)
        
        result_token = user.get_token()
        assert_that(result_token).is_equal_to(expected_token)

    def test_should_get_token_when_token_is_not_exist(self):
        user = baker.make('users.User')

        assert_that(Token.objects.filter(user=user).exists()).is_false()

        result_token = user.get_token()

        assert_that(result_token).is_equal_to(Token.objects.get(user=user))
