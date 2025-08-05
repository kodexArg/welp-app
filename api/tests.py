from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase


class HelloWorldAPITest(APITestCase):
    def test_hello_world(self):
        url = reverse('hello_world')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'hello world')
