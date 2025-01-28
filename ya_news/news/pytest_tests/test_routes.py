import pytest
from http import HTTPStatus
from typing import Optional
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_comment_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_comment_for_args')),
    )
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    name: str,
    args: tuple,
    expected_status
) -> None:
    """Тест на доступность редактирования и удаления комментария"""
    url: str = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db()
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_new_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_availability_for_anonymous_user(
    client,
    name: str,
    args: Optional[dict],
) -> None:
    """Тест на доступность страниц анонимным пользователем"""
    url: str = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_comment_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_comment_for_args')),
    ),
)
def test_redirect_for_anonymous_client(
    client,
    name: str,
    args: tuple,
) -> None:
    """Тест на перенаправления на страницу входа"""
    login_url: str = reverse('users:login')
    url: str = reverse(name, args=args)
    expected_url: str = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
