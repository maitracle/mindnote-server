from django.db import models
from commons.models import BaseModel


class Article(BaseModel):
    user = models.ForeignKey('users.User', related_name='articles', on_delete=models.CASCADE)
    subject = models.CharField(max_length=512)
    description = models.CharField(max_length=512, blank=True)
    body = models.TextField(blank=True)


class Note(BaseModel):
    article = models.ForeignKey('articles.Article', related_name='notes', on_delete=models.CASCADE)
    contents = models.TextField(blank=True)


class Connection(BaseModel):
    article = models.ForeignKey('articles.Article', related_name='connections', on_delete=models.CASCADE)
    left_note = models.ForeignKey('articles.Note', related_name='connections_as_left_side', on_delete=models.CASCADE)
    right_note = models.ForeignKey('articles.Note', related_name='connections_as_right_side', on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
