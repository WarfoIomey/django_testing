import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db()
def test_news_count(
    ten_news,
    client,
) -> None:
    """Тест на корректность количества отображаемых новостей"""
    url: str = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count: int = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db()
def test_news_order(
    ten_news,
    client,
) -> None:
    """Тест на корректность порядка отображения новостей"""
    url: str = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates: list = [news.date for news in object_list]
    sorted_dates: list = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(
    author_client,
    many_comments,
) -> None:
    """Тест на корректность порядка отображения комментариев"""
    url: str = reverse('news:detail', args=(many_comments.pk, ))
    response = author_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps: list = [comment.created for comment in all_comments]
    sorted_timestamps: list = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db()
def test_anonymous_client_has_no_form(
    client,
    pk_new_for_args: tuple,
) -> None:
    """Тест на отображение формы у анонимных пользователей"""
    url: str = reverse('news:detail', args=pk_new_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(
    author_client,
    pk_new_for_args: tuple,
) -> None:
    """Тест на отображение формы у залогиненых пользователей"""
    url: str = reverse('news:detail', args=pk_new_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
