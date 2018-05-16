import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostModelTests(TestCase):

    def test_was_published_recently_with_future_post(self):
        """
        was_published_recently() returns False for posts whose published_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_post = Post(published_date=time)
        self.assertIs(future_post.was_published_recently(), False)

    def test_was_published_recently_with_old_post(self):
        """
        was_published_recently() returns False for posts whose published_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_post = Post(published_date=time)
        self.assertIs(old_post.was_published_recently(), False)

    def test_was_published_recently_with_recent_post(self):
        """
        was_published_recently() returns True for posts whose published_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_post = Post(published_date=time)
        self.assertIs(recent_post.was_published_recently(), True)


def setup_test_user():
    from django.contrib.auth.models import User
    if User.objects.filter(username='Tester').exists():
        user = User.objects.get(username='Tester')
    else:
        user = User.objects.create_user(username='Tester', email='test@test.com', password='test')

    return user


def create_post(user, post_title, post_text, days):
    """
    Create a post with the given `title`, 'text' and published the
    given number of `days` offset to now (negative for posts published
    in the past, positive for posts that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Post.objects.create(author=user,
                               title=post_title,
                               text=post_text,
                               created_date=timezone.now(),
                               published_date=time)


class PostIndexViewTests(TestCase):

    def test_no_posts(self):
        """
        If no posts exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['post_list'], [])

    def test_past_post(self):
        """
        Posts with a published_date in the past are displayed on the
        index page.
        """
        user = setup_test_user()

        create_post(user=user, post_title="Past post.", post_text="Past post.", days=-30)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['post_list'],
            ['<Post: Past post.>']
        )

    def test_future_post(self):
        """
        Posts with a published_date in the future aren't displayed on
        the index page.
        """
        user = setup_test_user()

        create_post(user=user, post_title="Future post.", post_text="Past post.", days=30)
        response = self.client.get(reverse('blog:index'))
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['post_list'], [])

    def test_future_post_and_past_post(self):
        """
        Even if both past and future posts exist, only past posts
        are displayed.
        """
        user = setup_test_user()

        create_post(user=user, post_title="Past post.", post_text="Past post.", days=-30)
        create_post(user=user, post_title="Future post.", post_text="Future post.", days=30)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['post_list'],
            ['<Post: Past post.>']
        )

    def test_two_past_post(self):
        """
        The posts index page may display multiple posts.
        """
        user = setup_test_user()

        create_post(user=user, post_title="Past post 1.", post_text="Past post 1.", days=-30)
        create_post(user=user, post_title="Past post 2.", post_text="Past post 2.", days=-5)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['post_list'],
            ['<Post: Past post 2.>', '<Post: Past post 1.>']
        )


class PostDetailViewTests(TestCase):

    def test_future_post(self):
        """
        The detail view of a post with a published_date in the future
        returns a 404 not found.
        """
        user = setup_test_user()

        future_post = create_post(user=user, post_title="Future post 1.", post_text="Future post 1.", days=5)
        url = reverse('blog:detail', args=(future_post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_post(self):
        """
        The detail view of a post with a published_date in the past
        displays the post's text.
        """
        user = setup_test_user()

        past_post = create_post(user=user, post_title="Past post 1.", post_text="Past post 1.", days=-5)
        url = reverse('blog:detail', args=(past_post.id,))
        response = self.client.get(url)
        self.assertContains(response, past_post.text)