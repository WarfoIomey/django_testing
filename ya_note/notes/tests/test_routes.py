from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class FixtureSetUpTestData(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.another_author = User.objects.create(username='warfolomey')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Первая заметка',
            text='Первые подробности',
            slug='hello',
            author=cls.author,
        )
        cls.url_list = 'notes:list'
        cls.url_done = 'notes:success'
        cls.url_add = 'notes:add'
        cls.url_delete = 'notes:delete'
        cls.url_detail = 'notes:detail'
        cls.url_edit = 'notes:edit'
        cls.url_home = 'notes:home'
        cls.url_login = 'users:login'
        cls.url_logout = 'users:logout'
        cls.url_signup = 'users:signup'


class TestRoutes(FixtureSetUpTestData):

    def test_pages_availability_user(self) -> None:
        """Тест на доступность пользователя на list, done, add."""
        urls: tuple = (
            (self.url_list, None),
            (self.url_done, None),
            (self.url_add, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url: str = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_anonymus(self) -> None:
        """Тест доступности страниц анонимных пользователей."""
        urls: tuple = (
            (self.url_home, None),
            (self.url_login, None),
            (self.url_logout, None),
            (self.url_signup, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url: str = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect(self) -> None:
        """Перенаправления анонимного пользователя на вход."""
        login_url: str = reverse('users:login')
        urls_args = (
            (self.url_list, None),
            (self.url_done, None),
            (self.url_add, None),
            (self.url_delete, (self.note.slug, )),
            (self.url_detail, (self.note.slug, )),
            (self.url_edit, (self.note.slug, )),
        )
        for address, args in urls_args:
            with self.subTest():
                url: str = reverse(address, args=args)
                redirect_url: str = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self) -> None:
        """Тест на доступность редактирования и удаления заметки."""
        users_statuses: tuple = (
            (self.author, HTTPStatus.OK),
            (self.another_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (self.url_edit, self.url_delete, self.url_detail):
                with self.subTest(user=user, name=name):
                    url: str = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
