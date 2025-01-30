from http import HTTPStatus

from .fixture import FixtureSetUpTestData


class TestRoutes(FixtureSetUpTestData):

    def test_pages_availability_anonymus(self) -> None:
        """Тесты доступности страниц."""
        urls_clients: tuple = (
            (self.home_url, self.client),
            (self.login_url, self.client),
            (self.logout_url, self.client),
            (self.signup_url, self.client),
            (self.list_url, self.client_author),
            (self.done_url, self.client_author),
            (self.add_url, self.client_author),
        )
        for url, client in urls_clients:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect(self) -> None:
        """Перенаправления анонимного пользователя на вход."""
        urls: list = [
            self.list_url,
            self.done_url,
            self.add_url,
            self.delete_url,
            self.detail_url,
            self.update_url,
        ]
        for url in urls:
            with self.subTest(url=url):
                redirect_url: str = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self) -> None:
        """Тест на доступность редактирования и удаления заметки."""
        users_statuses_clients: tuple = (
            (
                self.author,
                HTTPStatus.OK,
                self.client_author
            ),
            (
                self.another_author,
                HTTPStatus.NOT_FOUND,
                self.another_author_client
            ),
        )
        for user, status, client in users_statuses_clients:
            for url in (self.update_url, self.delete_url, self.detail_url):
                with self.subTest(user=user, url=url, client=client):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)
