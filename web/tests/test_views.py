from django.test import TestCase
from django.urls import reverse

from web.models import Message


class HomeViewTests(TestCase):
    def test_home_renders(self):
        response = self.client.get(reverse("web:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world!")

    def test_home_lists_messages(self):
        Message.objects.create(text="first message")
        response = self.client.get(reverse("web:home"))
        self.assertContains(response, "first message")
