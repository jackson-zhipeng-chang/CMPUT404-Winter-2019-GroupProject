from django.test import Client, TestCase
from django.urls import reverse
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User
from django.db.models import Q

class TestFriendRequestHandler(TestCase):
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

    def test_friend_request(self):
        # test send a new friend request
        url = reverse('friendrequest')
        response = self.client1.post(url,{
            "query":"friendrequest",
            "author":{
                "id":self.author1.id,
                "host":self.author1.host,
                "displayName":self.author1.displayName,
                "url":self.author1.host+'/'+str(self.author1.id)
            },
            "friend":{
                "id": self.author2.id,
                "host": self.author2.host,
                "displayName": self.author2.displayName,
                "url": self.author2.host + '/' + str(self.author2.id)
            }
        },'application/json')
        author = Author.objects.get(pk=self.author1.id)
        friend = Author.objects.get(pk=self.author2.id)
        has_friend_request = Friend.objects.filter(author=author,friend=friend).exists()
        self.assertTrue(has_friend_request)
        friend_request = Friend.objects.get(author=author,friend=friend)
        fr_id = friend_request.id
        self.assertEquals(response.status_code,200)

        # test get a friend request
        response = self.client2.get(url)
        self.assertEquals(response.status_code,200)
        get_fr_id=json.loads(response.content)[0]['id']
        self.assertEquals(str(fr_id),get_fr_id)

        # test accept this friend request
        friend_request_id = Friend.objects.get(author=author,friend=friend).id
        response = self.client2.put(url,{
            "id" : friend_request_id,
            "status":"Accept"
        },"application/json")
        self.assertEquals(response.status_code,200)
        is_accept = Friend.objects.get(author=author,friend=friend,status="Accept")
        self.assertTrue(is_accept)

        # test decline this friend request
        response = self.client2.put(url,{
            "id":friend_request_id,
            "status":"Decline"
        },"application/json")
        self.assertEquals(response.status_code,200)
        is_decline = Friend.objects.get(author=author,friend=friend,status="Decline")
        self.assertTrue(is_decline)

    def test_get_my_friend_and_unFriend(self):
        url = reverse('friendrequest')
        self.client1.post(url, {
            "query": "friendrequest",
            "author": {
                "id": self.author1.id,
                "host": self.author1.host,
                "displayName": self.author1.displayName,
                "url": self.author1.host + '/' + str(self.author1.id)
            },
            "friend": {
                "id": self.author2.id,
                "host": self.author2.host,
                "displayName": self.author2.displayName,
                "url": self.author2.host + '/' + str(self.author2.id)
            }
        }, 'application/json')
        author = Author.objects.get(pk=self.author1.id)
        friend = Author.objects.get(pk=self.author2.id)
        friend_request_id = Friend.objects.get(author=author,friend=friend).id

        self.client2.put(url, {
            "id": friend_request_id,
            "status": "Accept"
        }, "application/json")

        get_friend_url = reverse('myfriends')
        response=self.client1.get(get_friend_url)
        self.assertEquals(response.status_code,200)
        self.assertEquals(json.loads(response.content)[0]['id'],str(self.author2.id))

        delete_url = reverse('unfriend',args=[self.author1.id])
        response = self.client2.delete(delete_url)
        self.assertTrue(response.status_code,200)
        has_friend = Friend.objects.filter(author=author,friend=friend).exists()
        self.assertFalse(has_friend)