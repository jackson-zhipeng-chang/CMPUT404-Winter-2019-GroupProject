from django.test import SimpleTestCase
from myBlog.views import NewPostHandler,PostHandler
from django.urls import reverse,resolve


# class TestUrls(SimpleTestCase):
#     def test_urls_new_post(self):
#         url = reverse("new_post")
#         self.assertEquals(resolve(url).func.view_class,NewPostHandler)

