from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotePage(TestCase):

    HOME_URL: str = reverse('notes:list')

    @classmethod
    def setUpTestData(cls) -> None:
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

    def test_notes_order(self) -> None:
        """Тест на отображения заметок по возрастанию"""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_id: list = [notes.id for notes in object_list]
        sorted_id: list = sorted(all_id)
        self.assertEqual(all_id, sorted_id)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.another_author = User.objects.create(username='Danil')
        cls.note = Note.objects.create(
            title='заметка',
            text='просто текст',
            slug='hello',
            author=cls.author,
        )
        cls.note_another = Note.objects.create(
            title='Это замека Danil',
            text='просто текст',
            slug='danil',
            author=cls.another_author,
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.update_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_list_author_note(self) -> None:
        """Тест на получение только заметок автора"""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertNotIn(self.note_another, response.context['object_list'])

    def test_authorized_client_has_form_create(self) -> None:
        """Тест на отображения формы создания заметки"""
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_form_update(self) -> None:
        """Тест на отображение формы на редактирования заметки"""
        self.client.force_login(self.author)
        response = self.client.get(self.update_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
