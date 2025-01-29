from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class FixtureSetUpTestData(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.another_author = User.objects.create(username='Danil')
        cls.note = Note.objects.create(
            title='заметка топ',
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
        cls.urls_forms = (
            (cls.add_url, NoteForm),
            (cls.update_url, NoteForm),
        )


class TestDetailPage(FixtureSetUpTestData):

    def test_separate_note(self) -> None:
        """Тест на передачу отдельной заметки в context."""
        response = self.client_author.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_list_author_note(self) -> None:
        """Тест на получение только заметок автора."""
        response = self.client_author.get(self.list_url)
        self.assertNotIn(self.note_another, response.context['object_list'])

    def test_authorized_client_has_form_create_update(self) -> None:
        """Тест на отображения формы создания и редактирования заметки."""
        for url, form in self.urls_forms:
            with self.subTest():
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], form)
