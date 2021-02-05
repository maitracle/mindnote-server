import json

from assertpy import assert_that
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article


class ArticlesViewSetTestCase(APITestCase):
    def test_create_article(self):
        article_data = {
            'subject': 'test subject',
            'description': 'test description'
        }
        user = baker.make('users.User')

        self.client.force_authenticate(user=user)
        response = self.client.post('/articles/', data=json.dumps(article_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)

        article = Article.objects.get(id=response.data['id'])

        assert_that(response.data['user']).is_equal_to(article.user.id)
        assert_that(response.data['user']).is_equal_to(user.id)
        assert_that(response.data['subject']).is_equal_to(article_data['subject'])
        assert_that(response.data['description']).is_equal_to(article_data['description'])

    def test_should_not_create_bad_request(self):
        article_data = {
            'description': 'test description'
        }
        user = baker.make('users.User')

        self.client.force_authenticate(user=user)
        response = self.client.post('/articles/', data=json.dumps(article_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)

    def test_should_not_create_unauthorized(self):
        article_data = {
            'subject': 'test subject',
            'description': 'test description'
        }

        response = self.client.post('/articles/', data=json.dumps(article_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)

    def test_should_get_own_list(self):
        user = baker.make('users.User')
        article_quantity = 5
        articles = baker.make('articles.Article', user=user, _quantity=article_quantity)

        self.client.force_authenticate(user=user)
        response = self.client.get('/articles/my-list/')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.data).is_length(article_quantity)
        for response_article, expected_article in zip(response.data, articles):
            self._assert_article(response_article, expected_article)

    def test_should_not_get_own_list_unauthorized(self):
        baker.make('articles.Article', _quantity=5)
        response = self.client.get('/articles/my-list/')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)

    def test_should_retrieve(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)

        self.client.force_authenticate(user=user)
        response = self.client.get(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        self._assert_article(response.data, article)
        assert_that(response.data['notes']).is_equal_to([])

    def test_should_retrieve_with_notes_and_connections(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        own_notes_quantity = 5
        another_user_notes_quantity = 7
        own_notes = baker.make('articles.Note', article=article, _quantity=own_notes_quantity)
        _another_user_notes = baker.make('articles.Note', _quantity=another_user_notes_quantity)
        own_connections_quantity = 4
        another_user_connections_quantity = 6
        own_connections = baker.make('articles.Connection', article=article, _quantity=own_connections_quantity)
        _another_user_connections = baker.make('articles.Connection', _quantity=another_user_connections_quantity)

        self.client.force_authenticate(user=user)
        response = self.client.get(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        self._assert_article(response.data, article)

        assert_that(response.data['notes']).is_length(own_notes_quantity)
        for response_note, expected_note in zip(response.data['notes'], own_notes):
            assert_that(response_note['id']).is_equal_to(expected_note.id)
            assert_that(response_note['article']).is_equal_to(article.id)
            assert_that(response_note['contents']).is_equal_to(expected_note.contents)

        for response_connection, expected_connection in zip(response.data['connections'], own_connections):
            assert_that(response_connection['id']).is_equal_to(expected_connection.id)
            assert_that(response_connection['article']).is_equal_to(article.id)
            assert_that(response_connection['left_note']).is_equal_to(expected_connection.left_note.id)
            assert_that(response_connection['right_note']).is_equal_to(expected_connection.right_note.id)
            assert_that(response_connection['reason']).is_equal_to(expected_connection.reason)

    def test_should_not_retrieve_unauthorized(self):
        article = baker.make('articles.Article')

        response = self.client.get(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)

    def test_should_not_retrieve_forbidden(self):
        user = baker.make('users.User')
        origin_article = baker.make('articles.Article')
        assert_that(user.id).is_not_equal_to(origin_article.user.id)

        self.client.force_authenticate(user=user)
        response = self.client.get(f'/articles/{origin_article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)

    def test_should_update(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        update_data = {
            'subject': 'changed subject',
        }

        self.client.force_authenticate(user=user)
        response = self.client.patch(f'/articles/{article.id}/', data=json.dumps(update_data),
                                      content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        changed_article = Article.objects.get(id=article.id)
        assert_that(changed_article.subject).is_equal_to(update_data['subject'])
        self._assert_article(response.data, changed_article)

    def test_should_not_update_unauthorized(self):
        origin_article = baker.make('articles.Article')
        update_data = {
            'subject': 'changed subject',
        }

        response = self.client.patch(f'/articles/{origin_article.id}/', data=json.dumps(update_data),
                                      content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        not_changed_article = Article.objects.get(id=origin_article.id)
        assert_that(not_changed_article.subject).is_equal_to(origin_article.subject)

    def test_should_not_update_forbidden(self):
        user = baker.make('users.User')
        origin_article = baker.make('articles.Article')
        assert_that(user.id).is_not_equal_to(origin_article.user.id)

        update_data = {
            'subject': 'changed subject',
        }

        self.client.force_authenticate(user=user)
        response = self.client.patch(f'/articles/{origin_article.id}/', data=json.dumps(update_data),
                                      content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        not_changed_article = Article.objects.get(id=origin_article.id)
        assert_that(not_changed_article.subject).is_equal_to(origin_article.subject)

    def test_should_delete(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)

        self.client.force_authenticate(user=user)
        response = self.client.delete(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_204_NO_CONTENT)
        assert_that(Article.objects.filter(id=article.id).exists()).is_false()

    def test_should_not_delete_unauthorized(self):
        article = baker.make('articles.Article')

        response = self.client.delete(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        assert_that(Article.objects.filter(id=article.id).exists()).is_true()

    def test_should_not_delete_forbidden(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article')
        assert_that(user.id).is_not_equal_to(article.user.id)

        self.client.force_authenticate(user=user)
        response = self.client.delete(f'/articles/{article.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        assert_that(Article.objects.filter(id=article.id).exists()).is_true()

    @staticmethod
    def _assert_article(response_article, expected_article):
        assert_that(response_article['user']).is_equal_to(expected_article.user.id)
        assert_that(response_article['subject']).is_equal_to(expected_article.subject)
        assert_that(response_article['description']).is_equal_to(expected_article.description)
