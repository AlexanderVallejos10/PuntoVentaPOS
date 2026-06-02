from django.test import TestCase


class HomeViewTests(TestCase):

    def test_home_requires_authentication(self):
        response = self.client.get('/')

        self.assertRedirects(response, '/login/?next=/')
