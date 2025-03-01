from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class FixtureSetUpTestData(TestCase):
    ONE_NOTE: int = 1

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='warfolomey')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.another_author = User.objects.create(username='Danil')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
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
        cls.done_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.update_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.urls_forms = (
            (cls.add_url, NoteForm),
            (cls.update_url, NoteForm),
        )
        cls.form_data = {
            'title': 'Test',
            'text': 'Просто текст',
            'slug': 'test',
        }

    def get_note(self, id_note):
        """Метод получения заметки по id."""
        return Note.objects.get(id=id_note)
