from http import HTTPStatus

from django.contrib.auth import get_user
from pytils.translit import slugify

from notes.forms import WARNING
from .fixture import FixtureSetUpTestData
from notes.models import Note


class TestNoteCreation(FixtureSetUpTestData):

    def test_empty_slug(self):
        """Тест на незаполненный slug."""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.client_author.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        assert Note.objects.count() == self.ONE_NOTE
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug

    def test_anonymous_user_cant_create_note(self) -> None:
        """Тест на создания заметки анонимным пользователем."""
        later_count_notes: int = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, later_count_notes)

    def test_user_can_create_note(self) -> None:
        """Тест на создания заметки залогиненым пользователем."""
        Note.objects.all().delete()
        response = self.client_author.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, self.ONE_NOTE)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, get_user(self.client_author))


class TestNoteEditDelete(FixtureSetUpTestData):

    def test_author_can_delete_note(self) -> None:
        """Тест на удаление автором заметки."""
        later_count_notes: int = Note.objects.count()
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, later_count_notes - self.ONE_NOTE)

    def test_user_cant_delete_note_of_another_user(self) -> None:
        """Тест на удаление заметки другим пользователем."""
        later_notes_count: int = Note.objects.count()
        response = self.another_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, later_notes_count)

    def test_author_can_edit_note(self) -> None:
        """Тест на редактирования автором заметки."""
        response = self.client_author.post(
            self.update_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.done_url)
        new_note = self.get_note(self.note.id)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.note.author)

    def test_not_unique_slug(self) -> None:
        """Тест на уникальность slug."""
        self.form_data['slug'] = self.note.slug
        response = self.client_author.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_user_cant_edit_note_of_another_user(self) -> None:
        """Тест на редактирования заметки другого автора."""
        response = self.another_author_client.post(
            self.update_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_note = self.get_note(self.note.id)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.slug, new_note.slug)
        self.assertEqual(self.note.author, new_note.author)
