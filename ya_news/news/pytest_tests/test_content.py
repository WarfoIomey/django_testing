import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(
    ten_news,
    url_reverse_home,
    client,
) -> None:
    """Тест на корректность количества отображаемых новостей."""
    response = client.get(url_reverse_home)
    object_list = response.context['object_list']
    news_count: int = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(
    ten_news,
    url_reverse_home,
    client,
) -> None:
    """Тест на корректность порядка отображения новостей."""
    response = client.get(url_reverse_home)
    all_dates: list = [news.date for news in response.context['object_list']]
    sorted_dates: list = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(
    author_client,
    url_reverse_detail,
    many_comments,
) -> None:
    """Тест на корректность порядка отображения комментариев."""
    response = author_client.get(url_reverse_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps: list = [comment.created for comment in all_comments]
    sorted_timestamps: list = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(
    client,
    url_reverse_detail,
) -> None:
    """Тест на отображение формы у анонимных пользователей."""
    response = client.get(url_reverse_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(
    author_client,
    url_reverse_detail,
) -> None:
    """Тест на отображение формы у залогиненых пользователей."""
    response = author_client.get(url_reverse_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
