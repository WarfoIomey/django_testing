from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotePage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='warfolomey')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'{index}',
                author=cls.author,
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_id = [notes.id for notes in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='warfolomey')
        cls.note = Note.objects.create(
            title='заметка',
            text='просто текст',
            slug='hello',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.update_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_form_create(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_update(self):
        self.client.force_login(self.author)
        response = self.client.get(self.update_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
