from django.test import Client, TestCase
from django.urls import reverse
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User


class TestViews(TestCase):
    def setUp(self):
        # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
        self.user = User.objects.create(username='testuser')
        self.user.set_password('test')

        self.user.save()
        self.client = Client()
        self.client.login(username='testuser', password='test')

        self.new_post_url = reverse('new_post')


    def test_new_post_Handler_POST_API(self):
        author = Author.objects.create(user=self.user)

        response = self.client.post(self.new_post_url,{
            'title': 'POST1',
            'description': 'post for testing',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
            'content': 'test'
        })
        self.assertEquals(response.status_code,200)