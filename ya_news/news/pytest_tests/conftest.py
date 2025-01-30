from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Автор комментария"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Пользователь который не оставлял комментарии"""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def new():
    """Создание новости"""
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def ten_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(new, author):
    """Создание комментария"""
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def many_comments(new, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()



@pytest.fixture
def url_reverse_home() -> str:
    return reverse('news:home')


@pytest.fixture
def url_reverse_login() -> str:
    return reverse('users:login')


@pytest.fixture
def url_reverse_signup() -> str:
    return reverse('users:login')


@pytest.fixture
def url_reverse_logout() -> str:
    return reverse('users:login')


@pytest.fixture
def url_reverse_detail(new) -> str:
    return reverse('news:detail', args=(new.pk,))


@pytest.fixture
def url_reverse_edit(comment) -> str:
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def url_reverse_delete(comment) -> str:
    return reverse('news:delete', args=(comment.pk,))
