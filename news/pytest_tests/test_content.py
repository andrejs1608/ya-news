import pytest

from django.urls import reverse

from pytest_lazy_fixtures import lf


def test_news_count(client, news_url, news_list):
    """Проверка количества новостей на странице."""
    response = client.get(news_url)
    object_list = response.context['object_list']
    assert len(object_list) == len(news_list)


def test_news_order(client, news_url):
    """Проверка порядка новостей на странице."""
    response = client.get(news_url)
    object_list = response.context['object_list']
    ids = [news.id for news in object_list]
    assert ids == sorted(ids)


def test_comments_order(client, news_url, comments):
    """Проверка порядка комментариев на странице новости."""
    response = client.get(news_url)
    news = response.context['object_list'][0]
    comments_list = list(news.comment_set.order_by('created'))
    assert len(comments_list) >= 2
    comments_in_order = [comment.created for comment in comments_list]
    assert comments_in_order == sorted(comments_in_order)


@pytest.mark.django_db 
@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (lf('author_client'), True),
        (lf('client'), False),
    ),
)
def test_form_availability_for_different_users(
        news, parametrized_client, form_in_page
):
    """Проверка наличия формы для авторизованного и неавторизованного пользователя."""
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_page