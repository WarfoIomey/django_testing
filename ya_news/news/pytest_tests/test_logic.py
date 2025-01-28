import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db()
def test_anonymous_user_cant_create_comment(
    client,
    pk_new_for_args,
    form_data: dict,
) -> None:
    """Тест на создания комментария анонимным пользователем"""
    url: str = reverse('news:detail', args=pk_new_for_args)
    client.post(url, data=form_data)
    comments_count: int = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author_client,
    new,
    form_data: dict,
    get_author,
) -> None:
    """Тест на создания комментария залогиненому пользователем"""
    url: str = reverse('news:detail', args=(new.pk, ))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count: int = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news.pk == new.pk
    assert comment.author == get_author


def test_user_cant_use_bad_words(
    author_client,
    bad_words: tuple,
    pk_new_for_args: tuple,
) -> None:
    """Тест на запрет использования запрещенных слов"""
    url: str = reverse('news:detail', args=pk_new_for_args)
    for words in bad_words:
        form_data: dict = {'text': f'Ты похож на {words}'}
        response = author_client.post(url, data=form_data)
        assertFormError(response, 'form', 'text', errors=WARNING)
        comments_count: int = Comment.objects.count()
        assert comments_count == 0


def test_author_can_delete_comment(
    author_client,
    pk_comment_for_args: tuple,
    pk_new_for_args: tuple,
) -> None:
    """Тест на удаление комментария автором"""
    url_comment: str = reverse('news:delete', args=pk_comment_for_args)
    url_new: str = reverse('news:detail', args=pk_new_for_args)
    response = author_client.delete(url_comment)
    assertRedirects(response, f'{url_new}#comments')
    comments_count: int = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    reader_client,
    pk_comment_for_args: tuple,
) -> None:
    """Тест на удаление чужого комментария"""
    url_comment: str = reverse('news:delete', args=pk_comment_for_args)
    response = reader_client.delete(url_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count: int = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client,
    form_data: dict,
    new,
    comment,
) -> None:
    """Тест на изменения комментария автором"""
    url_edit: str = reverse('news:edit', args=(comment.pk, ))
    url_new: str = reverse('news:detail', args=(new.pk, ))
    response = author_client.post(url_edit, data=form_data)
    assertRedirects(response, f'{url_new}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    form_data: dict,
    comment,
) -> None:
    url_edit: str = reverse('news:edit', args=(comment.pk, ))
    response = reader_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
