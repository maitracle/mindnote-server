from django.contrib import admin
from django.contrib.admin import register

from articles.models import Article, Note


@register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass
