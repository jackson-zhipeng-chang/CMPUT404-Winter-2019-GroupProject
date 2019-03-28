from django.test import Client, TestCase
from django.urls import reverse
import json
from myBlog.models import Author,Friend
from django.contrib.auth.models import User

class TestFriendToFriendHandler(TestCase):
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
                                            host='http://127.0.0.1:7000',
                                            github='https://github.com/terrence85561')

    def test_get_friend_to_friend(self):
        author1_id = self.author1.id
        author2_id = self.author2.id
        author2_host = self.author2.host
        service2 = author2_host.split('/')[2]
        url = reverse('friend2friend',kwargs={'authorid1':str(author1_id),'service2':str(service2),'authorid2':str(author2_id)})
        response=self.client1.get(url)
        self.assertEquals(response.status_code,200)
        isFriend=json.loads(response.content)['friends']
        self.assertFalse(isFriend)

        wrong_uuid = 'de305d54-75b4-431b-adb2-eb6b9e546013'
        wrong_url = reverse('friend2friend',kwargs={'authorid1':wrong_uuid,'service2':str(service2),'authorid2':str(author2_id)})
        response=self.client1.get(wrong_url)
        self.assertEquals(response.status_code,404)