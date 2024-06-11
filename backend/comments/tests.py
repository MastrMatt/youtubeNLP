from django.test import TestCase


# test for the views
class TestViews(TestCase):
    def test_comments_analysis_view(self):
        response = self.client.get("/LjQSxl0Nfrs")
        print(response)
