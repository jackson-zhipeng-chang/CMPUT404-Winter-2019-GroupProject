from django.test import SimpleTestCase
from myBlog.views import NewPostHandler,PostHandler,CommentHandler
from django.urls import reverse,resolve
import uuid


class TestUrls(SimpleTestCase):
    def test_urls_new_post(self):
        url = reverse("new_post")
        self.assertEquals(resolve(url).func.view_class,NewPostHandler)

    def test_urls_modify_post(self):
        post_id = uuid.uuid4()
        url = reverse("modify_post",args=[post_id])
        self.assertEquals(resolve(url).func.view_class,PostHandler)

    def test_urls_comment(self):
        post_id = uuid.uuid4()
        url = reverse('comment',args=[post_id])
        self.assertEquals(resolve(url).func.view_class,CommentHandler)