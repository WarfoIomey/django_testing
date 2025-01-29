from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('url_reverse_edit'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_reverse_delete'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_reverse_edit'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_reverse_delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_reverse_detail'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            reverse('news:home'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:login'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
    ),
)
def test_availability(
    reverse_url: str,
    parametrized_client,
    expected_status,
) -> None:
    """Тесты на доступность."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url',
    (
        pytest.lazy_fixture('url_reverse_edit'),
        pytest.lazy_fixture('url_reverse_delete'),
    ),
)
def test_redirect_for_anonymous_client(
    client,
    reverse_url: str,
) -> None:
    """Тест на перенаправления на страницу входа."""
    login_url: str = reverse('users:login')
    expected_url: str = f'{login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
