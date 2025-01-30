from .fixture import FixtureSetUpTestData


class TestDetailPage(FixtureSetUpTestData):

    def test_separate_note(self) -> None:
        """Тест на передачу отдельной заметки в context."""
        response = self.client_author.get(self.list_url)
        note = response.context['object_list']
        self.assertIn(self.note, note)

    def test_list_author_note(self) -> None:
        """Тест на получение только заметок автора."""
        response = self.client_author.get(self.list_url)
        self.assertNotIn(self.note_another, response.context['object_list'])

    def test_authorized_client_has_form_create_update(self) -> None:
        """Тест на отображения формы создания и редактирования заметки."""
        for url, form in self.urls_forms:
            with self.subTest(url=url, form=form):
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], form)
