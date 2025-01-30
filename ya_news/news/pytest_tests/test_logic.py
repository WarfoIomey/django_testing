from http import HTTPStatus

import pytest
from django.contrib.auth import get_user
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA: dict = {
    'text': 'Новый текст',
}
ONE_COMMENT: int = 1
pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client,
    url_reverse_detail,
) -> None:
    """Тест на создания комментария анонимным пользователем."""
    later_comments_count = Comment.objects.count()
    client.post(url_reverse_detail, data=FORM_DATA)
    comments_count: int = Comment.objects.count()
    assert comments_count == later_comments_count


def test_user_can_create_comment(
    author_client,
    url_reverse_detail,
    new,
) -> None:
    """Тест на создания комментария залогиненому пользователем."""
    Comment.objects.all().delete()
    response = author_client.post(url_reverse_detail, data=FORM_DATA)
    assertRedirects(response, f'{url_reverse_detail}#comments')
    comments_count: int = Comment.objects.count()
    assert comments_count == ONE_COMMENT
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news.pk == new.pk
    assert comment.author == get_user(author_client)


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(
    author_client,
    bad_word: str,
    url_reverse_detail,
) -> None:
    """Тест на запрет использования запрещенных слов."""
    later_comments_count = Comment.objects.count()
    form_data: dict = {'text': f'Ты похож на {bad_word}'}
    response = author_client.post(url_reverse_detail, data=form_data)
    comments_count: int = Comment.objects.count()
    assert comments_count == later_comments_count
    assertFormError(response, 'form', 'text', errors=WARNING)


def test_author_can_delete_comment(
    author_client,
    url_reverse_delete,
    url_reverse_detail,
) -> None:
    """Тест на удаление комментария автором."""
    later_comment_count = Comment.objects.count()
    response = author_client.delete(url_reverse_delete)
    assertRedirects(response, f'{url_reverse_detail}#comments')
    comments_count: int = Comment.objects.count()
    assert comments_count == later_comment_count - ONE_COMMENT


def test_user_cant_delete_comment_of_another_user(
    reader_client,
    url_reverse_delete,
) -> None:
    """Тест на удаление чужого комментария."""
    later_comment_count = Comment.objects.count()
    response = reader_client.delete(url_reverse_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count: int = Comment.objects.count()
    assert comments_count == later_comment_count


def test_author_can_edit_comment(
    author_client,
    url_reverse_detail,
    url_reverse_edit,
    comment,
) -> None:
    """Тест на изменения комментария автором."""
    response = author_client.post(url_reverse_edit, data=FORM_DATA)
    assertRedirects(response, f'{url_reverse_detail}#comments')
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    author_client,
    url_reverse_edit,
    comment,
) -> None:
    """Тест на изменения чужих комментариев."""
    response = reader_client.post(url_reverse_edit, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news
