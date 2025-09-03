from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Проверка доступности страниц для неавторизованного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_author(author_client, name, comment):
    """Проверка доступности страниц для автора."""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_anonimymous_user(client, name, comment):
    """Проверка редиректов для неавторизованного пользователя."""
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:edit', lf('news')),
        ('news:delete', lf('news')),
    ),
)
def test_redirects(client, name, news_object):
    """Проверка редиректов для неавторизованного пользователя."""
    login_url = reverse('users:login')
    if news_object is not None:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def authorized_client_cant_edit_other_users_comment(
        client, author, news, django_user_model
):
    """Проверка что авторизованный пользователь не может редактировать чужой комментарий."""
    another_user = django_user_model.objects.create(username='another_user')
    client.force_login(another_user)
    comment = comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )
    url = reverse('news:edit', args=(comment.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, reverse('news:home'))

@pytest.mark.django_db
def news_availability_for_anonymous_user(client, news_url):
    """Проверка доступности страницы со списком новостей для неавторизованного пользователя."""
    response = client.get(news_url)
    assert response.status_code == HTTPStatus.OK
