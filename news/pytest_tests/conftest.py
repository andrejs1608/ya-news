import pytest

from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='автор')

@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client

@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )
    return comment

@pytest.fixture
def news_url(news):
    return reverse('news:home')

@pytest.fixture
def news_list():
    News.objects.all().delete()
    return [
        News.objects.create(
            title=f'Новость {i}',
            text='Текст'
        ) for i in range(5)
    ]

@pytest.fixture
def comments(author, news):
    Comment.objects.all().delete()
    return [
        Comment.objects.create(
            text=f'Комментарий {i}',
            author=author,
            news=news,
        ) for i in range(2)
    ]


@pytest.fixture
def news_edit_url(news):
    return reverse('news:edit', args=(news.id,))

@pytest.fixture
def comments_url(news):
    return reverse('news:detail', args=(news.id,)) + '#comments'


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))
