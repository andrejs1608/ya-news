from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
        author_client, author, news
):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': 'comment'})
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == initial_comments_count + 1
    new_comment = Comment.objects.first()
    assert new_comment.text == 'comment'
    assert new_comment.author == author
    assert new_comment.author == author


def test_unauthorized_user_cannot_create_comment(
        client, news
):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data={'text': 'comment'}, follow=True)
    login_url = reverse('users:login')
    assertRedirects(response, f'{login_url}?next={url}')
    assert Comment.objects.count() == initial_comments_count


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_is_not_added(
        author_client, news, bad_word
):
    initial_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Этот комментарий содержит слово {bad_word}'}
    response = author_client.post(
        url, 
        data=bad_words_data,
        follow=True
    )
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == initial_comments_count


def test_author_can_edit_comment(
        author_client, comment, news_edit_url, comments_url
):
    response = author_client.post(
        news_edit_url,
        data={'text': 'Отредактированный комментарий'},
        follow=True
    )
    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == 'Отредактированный комментарий'


def test_unauthorized_user_cant_edit_comment(
        client, comment, news_edit_url
):
    response = client.post(
        news_edit_url,
        data={'text': 'Отредактированный комментарий'},
        follow=True
    )
    login_url = reverse('users:login')
    assertRedirects(response, f'{login_url}?next={news_edit_url}')
    comment.refresh_from_db()
    assert comment.text != 'Отредактированный комментарий'


def test_author_can_delete_comment(author_client, comment_delete_url, comments_url):
    initial_comments_count = Comment.objects.count()
    response = author_client.post(
        comment_delete_url,
        follow=True
    )
    assertRedirects(response, comments_url)
    assert Comment.objects.count() == initial_comments_count - 1


def test_unauthorized_user_cant_delete_comment(
        client, comment_delete_url
):
    initial_comments_count = Comment.objects.count()
    response = client.post(
        comment_delete_url,
        follow=True
    )
    login_url = reverse('users:login')
    assertRedirects(response, f'{login_url}?next={comment_delete_url}')
    assert Comment.objects.count() == initial_comments_count
