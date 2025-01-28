from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreationAutoSlug(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.note = Note.objects.create(
            title='Test',
            text='Text',
            author=cls.author,
        )

    def test_auto_slug(self) -> None:
        """Тест на авто подстановку slug"""
        note = Note.objects.get()
        self.assertEqual(self.note.slug, note.slug)


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.url = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Test',
            'text': 'Просто текст',
            'slug': 'test',
            'author': cls.author,
        }

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug

    def test_anonymous_user_cant_create_note(self) -> None:
        """Тест на создания заметки анонимным пользователем"""
        self.client.post(self.url, data=self.form_data)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self) -> None:
        """Тест на создания заметки залогиненым пользователем"""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.form_data['author'])


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.another_user = User.objects.create(username='Danil')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title='Test',
            text='Text',
            slug='test',
            author=cls.author,
        )
        cls.success = reverse('notes:success')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': 'edit test',
            'text': 'Просто текст',
            'slug': 'edit',
        }

    def test_author_can_delete_note(self) -> None:
        """Тест на удаление автором заметки"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self) -> None:
        """Тест на удаление заметки другим пользователем"""
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self) -> None:
        """Тест на редактирования автором заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'edit test')
        self.assertEqual(self.note.text, 'Просто текст')
        self.assertEqual(self.note.slug, 'edit')

    def test_not_unique_slug(self) -> None:
        """Тест на уникальность slug"""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_user_cant_edit_note_of_another_user(self) -> None:
        """Тест на редактирования заметки другого автора"""
        response = self.another_user_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Test')
        self.assertEqual(self.note.text, 'Text')
        self.assertEqual(self.note.slug, 'test')
