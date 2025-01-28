from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.another_author = User.objects.create(username='warfolomey')
        cls.note = Note.objects.create(
            title='Первая заметка',
            text='Первые подробности',
            slug='hello',
            author=cls.author,
        )

    def test_pages_availability_user(self) -> None:
        """Тест на доступность пользователя на list, done, add"""
        self.client.force_login(self.author)
        urls: tuple = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url: str = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_anonymus(self) -> None:
        """Тест доступности страниц анонимных пользователей"""
        urls: tuple = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url: str = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_change_note(self) -> None:
        """Перенаправления анонимного пользователя на вход с заметки"""
        login_url: str = reverse('users:login')
        for name in ('notes:delete', 'notes:detail', 'notes:edit'):
            with self.subTest(name=name):
                url: str = reverse(name, args=(self.note.slug,))
                redirect_url: str = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client(self) -> None:
        """Перенаправления анонимного пользователя"""
        login_url: str = reverse('users:login')
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url: str = reverse(name)
                redirect_url: str = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self) -> None:
        """Тест на доступность редактирования и удаления заметки"""
        users_statuses: tuple = (
            (self.author, HTTPStatus.OK),
            (self.another_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url: str = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
