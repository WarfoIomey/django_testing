import pytest

from django.test.client import Client
from django.conf import settings
from django.utils import timezone

from datetime import datetime, timedelta

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    """Автор комментария"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def get_author(author):
    return author


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
def comment(new, author):
    """Создание комментария"""
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def pk_comment_for_args(comment) -> tuple:
    return (comment.pk,)


@pytest.fixture
def pk_new_for_args(new) -> tuple:
    return (new.pk,)


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
    news = News.objects.bulk_create(all_news)
    return news

@pytest.fixture
def many_comments(new, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return new


@pytest.fixture
def form_data() -> dict:
    """Данные для комментария"""
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def bad_words() -> tuple:
    return BAD_WORDS
