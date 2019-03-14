from django.test import Client, TestCase
from django.urls import reverse
import uuid
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User
import datetime

class TestAuthorProfileHandler(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='testuser1')
        self.user1.set_password('test')
        self.user1.save()
        self.client1=Client()
        self.client1.login(username='testuser1',password='test')
        self.author1 = Author.objects.create(user=self.user1,displayName='author1',
                                            host='http://127.0.0.1:8000',
                                            github='https://github.com/terrence85561')

        self.user2 = User.objects.create(username='testuser2')
        self.user2.set_password('test')
        self.user2.save()
        self.client2 = Client()
        self.client2.login(username='testuser2', password='test')
        self.author2 = Author.objects.create(user=self.user2, displayName='author2',
                                            host='http://127.0.0.1:8000',
                                            github='https://github.com/terrence85561')

    def test_get_author_profile(self):
        # author2 visits author1's profile
        url = reverse('authorprofile',args=[self.author1.id])
        response = self.client2.get(url)
        self.assertEquals(response.status_code,200)
        author1_info = json.loads(response.content)
        self.assertEquals(author1_info['id'],str(self.author1.id))
        self.assertEquals(author1_info['host'],self.author1.host)
        self.assertEquals(author1_info['displayName'],self.author1.displayName)

    def test_put_author_profile(self):
        # author1 change author1's profile
        url = reverse('authorprofile',args=[self.author1.id])
        response = self.client1.put(url,{
            "displayName":'author1_change',
            'github':'https://github.com/terrence85561',
            'host':'http://127.0.0.1:8000',
            'url':'http://127.0.0.1:8000'+str(self.author1.id),
            'id':self.author1.id
        },'application/json')
        self.assertEquals(response.status_code,200)
        author1_info = json.loads(response.content)
        self.assertEquals(author1_info['displayName'],'author1_change')

        # author1 put invalid data
        response = self.client1.put(url, {
            'github': 'http://xxx.com',
            'host': 'http://127.0.0.1:5000',
            'url': 'http://127.0.0.1:5000' + str(self.author1.id),
            'id': self.author1.id
        }, 'application/json')
        self.assertEquals(response.status_code,400)

        # author2 want to change author1's profile
        response = self.client2.put(url,{
            "displayName":'author1_change',
            'github':'http://xxx.com',
            'host':'http://127.0.0.1:8000',
            'url':'http://127.0.0.1:8000'+str(self.author1.id),
            'id':self.author1.id
        },'application/json')
        self.assertEquals(response.status_code,404)

    def test_delet_author_profile(self):
        url = reverse('authorprofile',args=[self.author1.id])
        response=self.client1.delete(url)
        self.assertEquals(response.status_code,204)
        wrong_url = reverse('authorprofile',args=[self.author2.id])
        response=self.client1.delete(wrong_url)
        self.assertEquals(response.status_code,404)

    def test_get_my_profile(self):
        url = reverse('myprofile')
        response=self.client1.get(url)
        self.assertEquals(response.status_code,200)
        my_info = json.loads(response.content)
        self.assertEquals(my_info['displayName'],'author1')