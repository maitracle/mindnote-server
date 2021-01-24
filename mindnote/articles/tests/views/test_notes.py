import json

from assertpy import assert_that
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Note


class NotesViewSetTestCase(APITestCase):
    def test_create_note(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        note_data = {
            'article': article.id,
            'contents': 'test contents'
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/notes/', data=json.dumps(note_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)

        note = Note.objects.get(id=response.data['id'])

        assert_that(note.article.id).is_equal_to(note_data['article'])
        assert_that(note.contents).is_equal_to(note_data['contents'])

    def test_should_not_create_bad_request(self):
        user = baker.make('users.User')
        note_data = {
            'contents': 'test contents',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/notes/', data=json.dumps(note_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)

    def test_should_not_create_unauthorized(self):
        article = baker.make('articles.Article')
        note_data = {
            'article': article.id,
            'contents': 'test contents'
        }

        response = self.client.post('/articles/', data=json.dumps(note_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)

    def test_should_not_create_forbidden(self):
        user = baker.make('users.User')
        another_user_article = baker.make('articles.Article')
        note_data = {
            'article': another_user_article.id,
            'contents': 'test contents',
        }

        self.client.force_authenticate(user=user)
        response = self.client.post('/notes/', data=json.dumps(note_data), content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        assert_that(response.data['detail']).is_equal_to('note can be created at own article')

    def test_should_get_filtered_list(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        note_quantity = 5
        notes = baker.make('articles.Note', article=article, _quantity=note_quantity)
        _not_expected_notes = baker.make('articles.Note', _quantity=3)

        self.client.force_authenticate(user=user)
        response = self.client.get(f'/notes/?article={article.id}')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.data).is_length(note_quantity)
        for response_note, expected_note in zip(response.data, notes):
            self._assert_note(response_note, expected_note)

    def test_should_not_get_list_without_filter(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        note_quantity = 5
        _notes = baker.make('articles.Note', article=article, _quantity=note_quantity)
        _not_expected_notes = baker.make('articles.Note', _quantity=3)

        self.client.force_authenticate(user=user)
        response = self.client.get(f'/notes/')

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)

    def test_should_not_get_own_list_unauthorized(self):
        user = baker.make('users.User')
        article = baker.make('articles.Article', user=user)
        note_quantity = 5
        _notes = baker.make('articles.Note', article=article, _quantity=note_quantity)
        _not_expected_notes = baker.make('articles.Note', _quantity=3)

        response = self.client.get(f'/notes/?article={article.id}')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)

    def test_should_update(self):
        note = baker.make('articles.Note')
        update_data = {
            'contents': 'changed contents',
        }

        self.client.force_authenticate(user=note.article.user)
        response = self.client.patch(f'/notes/{note.id}/', data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        changed_note = Note.objects.get(id=note.id)
        assert_that(changed_note.contents).is_equal_to(update_data['contents'])
        self._assert_note(response.data, changed_note)

    def test_should_not_update_unauthorized(self):
        note = baker.make('articles.Note')
        update_data = {
            'contents': 'changed contents',
        }

        response = self.client.patch(f'/notes/{note.id}/', data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        not_changed_note = Note.objects.get(id=note.id)
        assert_that(not_changed_note.contents).is_equal_to(note.contents)

    def test_should_not_update_forbidden(self):
        note = baker.make('articles.Note')
        update_data = {
            'contents': 'changed contents',
        }
        another_user = baker.make('users.User')

        self.client.force_authenticate(user=another_user)
        response = self.client.patch(f'/notes/{note.id}/', data=json.dumps(update_data),
                                     content_type='application/json')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        not_changed_note = Note.objects.get(id=note.id)
        assert_that(not_changed_note.contents).is_equal_to(note.contents)

    def test_should_delete(self):
        note = baker.make('articles.Note')

        self.client.force_authenticate(user=note.article.user)
        response = self.client.delete(f'/notes/{note.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_204_NO_CONTENT)
        assert_that(Note.objects.filter(id=note.id).exists()).is_false()

    def test_should_not_delete_unauthorized(self):
        note = baker.make('articles.Note')

        response = self.client.delete(f'/notes/{note.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_401_UNAUTHORIZED)
        assert_that(Note.objects.filter(id=note.id).exists()).is_true()

    def test_should_not_delete_forbidden(self):
        note = baker.make('articles.Note')
        another_user = baker.make('users.User')

        self.client.force_authenticate(user=another_user)
        response = self.client.delete(f'/notes/{note.id}/')

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)
        assert_that(Note.objects.filter(id=note.id).exists()).is_true()

    @staticmethod
    def _assert_note(response_note, expected_note):
        assert_that(response_note['article']).is_equal_to(expected_note.article.id)
        assert_that(response_note['contents']).is_equal_to(expected_note.contents)
