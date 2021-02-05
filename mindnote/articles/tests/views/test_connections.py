import json

from assertpy import assert_that
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Connection


class ConnectionViewSetTestCase(APITestCase):
    def test_should_create_connection(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        notes = baker.make('articles.Note', article=article, _quantity=2)
        connection_data = {
            'article': article.id,
            'left_note': notes[0].id,
            'right_note': notes[1].id,
            'reason': 'test reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/connections/', data=json.dumps(connection_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)

        self._assert_connection(response.data, Connection.objects.get(id=response.data['id']))

    def test_should_not_create_connection_when_another_user_article(self):
        user = baker.make('users.User')
        another_user_article = baker.make('articles.Article')
        notes = baker.make('articles.Note', article=another_user_article, _quantity=2)
        connection_data = {
            'article': another_user_article.id,
            'left_note': notes[0].id,
            'right_note': notes[1].id,
            'reason': 'test reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/connections/', data=json.dumps(connection_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        assert_that(response.data['detail']).is_equal_to('connection can be created at own article')

    def test_should_not_create_connection_when_notes_are_same(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        note = baker.make('articles.Note', article=article)
        connection_data = {
            'article': article.id,
            'left_note': note.id,
            'right_note': note.id,
            'reason': 'test reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/connections/', data=json.dumps(connection_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.data['non_field_errors'][0]).is_equal_to("notes can't be same")

    def test_should_not_create_connection_when_notes_are_not_match_with_articles(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        matched_note = baker.make('articles.Note', article=article)
        not_matched_note = baker.make('articles.Note')
        connection_data = {
            'article': article.id,
            'left_note': matched_note.id,
            'right_note': not_matched_note.id,
            'reason': 'test reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/connections/', data=json.dumps(connection_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.data['non_field_errors'][0]).is_equal_to('notes and article are not matched')

    def test_should_not_create_connection(self):
        user = baker.make('users.User')
        notes = baker.make('articles.Note', _quantity=2)
        connection_data = {
            'left_note': notes[0].id,
            'right_note': notes[1].id,
            'reason': 'test reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/connections/', data=json.dumps(connection_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.data['article'][0]).is_equal_to('This field is required.')

    def test_should_update_connection(self):
        user = baker.make('users.User')
        connection = baker.make('articles.Connection', article__user=user)

        update_data = {
            'reason': 'changed reason',
        }

        self.client.force_authenticate(user=user)
        response = self.client.patch(f'/connections/{connection.id}/',
                                     data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        changed_connection = Connection.objects.get(id=connection.id)
        assert_that(changed_connection.reason).is_equal_to(update_data['reason'])
        self._assert_connection(response.data, changed_connection)

    def test_should_not_update_connection_unauthorized(self):
        origin_connection = baker.make('articles.Connection')
        update_data = {
            'reason': 'changed reason',
        }

        response = self.client.patch(f'/connections/{origin_connection.id}/',
                                     data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        not_changed_connection = Connection.objects.get(id=origin_connection.id)
        assert_that(not_changed_connection.reason).is_equal_to(origin_connection.reason)

    def test_should_not_update_connection_forbidden(self):
        another_user = baker.make('users.User')
        origin_connection = baker.make('articles.Connection')
        update_data = {
            'reason': 'changed reason',
        }

        self.client.force_authenticate(user=another_user)
        response = self.client.patch(f'/connections/{origin_connection.id}/',
                                     data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        not_changed_connection = Connection.objects.get(id=origin_connection.id)
        assert_that(not_changed_connection.reason).is_equal_to(origin_connection.reason)

    def test_should_delete_connection(self):
        user = baker.make('users.User')
        connection = baker.make('articles.Connection', article__user=user)

        self.client.force_authenticate(user=user)
        response = self.client.delete(f'/connections/{connection.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_204_NO_CONTENT)
        assert_that(Connection.objects.filter(id=connection.id).exists()).is_false()

    def test_should_not_delete_connection_unauthorized(self):
        connection = baker.make('articles.Connection')

        response = self.client.delete(f'/connections/{connection.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        assert_that(Connection.objects.filter(id=connection.id).exists()).is_true()

    def test_should_not_delete_connection_forbidden(self):
        another_user = baker.make('users.User')
        connection = baker.make('articles.Connection')

        self.client.force_authenticate(user=another_user)
        response = self.client.delete(f'/connections/{connection.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        assert_that(Connection.objects.filter(id=connection.id).exists()).is_true()

    @staticmethod
    def _assert_connection(response_connection, expected_connection):
        assert_that(response_connection['id']).is_equal_to(expected_connection.id)
        assert_that(response_connection['article']).is_equal_to(expected_connection.article.id)
        assert_that(response_connection['left_note']).is_equal_to(expected_connection.left_note.id)
        assert_that(response_connection['right_note']).is_equal_to(expected_connection.right_note.id)
        assert_that(response_connection['reason']).is_equal_to(expected_connection.reason)
