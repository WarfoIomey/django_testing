from http import HTTPStatus

from django.test import Client, TestCase
from django.contrib.auth import get_user_model, get_user
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class FixtureSetUpTestData(TestCase):
    ONE_NOTE: int = 1

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.another_user = User.objects.create(username='Danil')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title='Test',
            text='Text',
            slug='hello',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Test',
            'text': 'Просто текст',
            'slug': 'test',
        }
        cls.url_add = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))

    def get_note(self, id_note):
        """Метод получения заметки по id."""
        return Note.objects.get(id=id_note)


class TestNoteCreation(FixtureSetUpTestData):

    def test_empty_slug(self):
        """Тест на незаполненный slug."""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        assert Note.objects.count() == self.ONE_NOTE
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug

    def test_anonymous_user_cant_create_note(self) -> None:
        """Тест на создания заметки анонимным пользователем."""
        later_count_notes: int = Note.objects.count()
        self.client.post(self.url_add, data=self.form_data)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, later_count_notes)

    def test_user_can_create_note(self) -> None:
        """Тест на создания заметки залогиненым пользователем."""
        Note.objects.all().delete()
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, self.ONE_NOTE)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, get_user(self.author_client))


class TestNoteEditDelete(FixtureSetUpTestData):

    def test_author_can_delete_note(self) -> None:
        """Тест на удаление автором заметки."""
        later_count_notes: int = Note.objects.count()
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, later_count_notes - self.ONE_NOTE)

    def test_user_cant_delete_note_of_another_user(self) -> None:
        """Тест на удаление заметки другим пользователем."""
        response = self.another_user_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count: int = Note.objects.count()
        self.assertEqual(notes_count, self.ONE_NOTE)

    def test_author_can_edit_note(self) -> None:
        """Тест на редактирования автором заметки."""
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        new_note = self.get_note(self.note.id)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, get_user(self.author_client))

    def test_not_unique_slug(self) -> None:
        """Тест на уникальность slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_user_cant_edit_note_of_another_user(self) -> None:
        """Тест на редактирования заметки другого автора."""
        response = self.another_user_client.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_note = self.get_note(self.note.id)
        self.assertEqual(self.note.title, new_note.title)
        self.assertEqual(self.note.text, new_note.text)
        self.assertEqual(self.note.slug, new_note.slug)
        self.assertEqual(self.note.author, new_note.author)
