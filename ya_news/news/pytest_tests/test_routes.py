from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    (
        (lf('url_reverse_edit'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('url_reverse_delete'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('url_reverse_edit'), lf('author_client'), HTTPStatus.OK),
        (lf('url_reverse_delete'), lf('author_client'), HTTPStatus.OK),
        (lf('url_reverse_detail'), lf('client'), HTTPStatus.OK),
        (lf('url_reverse_home'), lf('client'), HTTPStatus.OK),
        (lf('url_reverse_login'), lf('client'), HTTPStatus.OK),
        (lf('url_reverse_logout'), lf('client'), HTTPStatus.OK),
        (lf('url_reverse_signup'), lf('client'), HTTPStatus.OK),
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
    'reverse_url, login_ulr',
    (
        (lf('url_reverse_edit'), lf('url_reverse_login')),
        (lf('url_reverse_delete'), lf('url_reverse_login')),
    ),
)
def test_redirect_for_anonymous_client(
    client,
    login_ulr,
    reverse_url: str,
) -> None:
    """Тест на перенаправления на страницу входа."""
    expected_url: str = f'{login_ulr}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
