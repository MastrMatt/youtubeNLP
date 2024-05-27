from django.test import TestCase
from rest_framework.test import APITestCase


class commentsAPITest(APITestCase):
    def test_get_comments(self):
        response = self.client.get("/comments/0_oCIabGeGE")
        self.assertEqual(response.status_code, 200)
