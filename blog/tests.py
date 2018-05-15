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
        future_question = Post(published_date=time)
        self.assertIs(future_question.was_published_recently(), False)

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


def create_post(post_title, post_text, days):
    """
    Create a post with the given `title`, 'text' and published the
    given number of `days` offset to now (negative for posts published
    in the past, positive for posts that have yet to be published).
    """
    from django.http import HttpRequest
    request = HttpRequest()
    time = timezone.now() + datetime.timedelta(days=days)
    return Post.objects.create(author=request.user,
                               title=post_title,
                               text=post_text,
                               created_date=datetime.now(),
                               published_date=time)


class PostIndexViewTests(TestCase):

    def test_no_posts(self):
        """
        If no posts exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_post(self):
        """
        Posts with a published_date in the past are displayed on the
        index page.
        """
        create_post(post_title="Past post.", post_text="Past post.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            ['<Question: Past question.>']
        )

    def test_future_post(self):
        """
        Posts with a published_date in the future aren't displayed on
        the index page.
        """
        create_post(post_title="Future post.", post_text="Past post.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['latest_Post_list'], [])

    def test_future_post_and_past_post(self):
        """
        Even if both past and future posts exist, only past posts
        are displayed.
        """
        create_post(post_title="Past post.", post_text="Past post.", days=-30)
        create_post(post_title="Future post.", post_text="Future post.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            ['<Post: Past question.>']
        )

    def test_two_past_post(self):
        """
        The posts index page may display multiple questions.
        """
        create_post(post_title="Past post 1.", post_text="Past post 1.", days=-30)

        create_post(post_title="Past post 2.", post_text="Past post 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_post_list'],
            ['<Post: Past question 2.>', '<Post: Past question 1.>']
        )


class PostDetailViewTests(TestCase):

    def test_future_post(self):
        """
        The detail view of a post with a published_date in the future
        returns a 404 not found.
        """
        future_post = create_post(post_title="Future post 1.", post_text="Future post 1.", days=5)
        url = reverse('polls:detail', args=(future_post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_post(self):
        """
        The detail view of a question with a published_date in the past
        displays the post's text.
        """
        past_post = create_post(post_title="Past post 1.", post_text="Past post 1.", days=-5)
        url = reverse('polls:detail', args=(past_post.id,))
        response = self.client.get(url)
        self.assertContains(response, past_post.text)