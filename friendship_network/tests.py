"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import User, FriendshipManager


class SimpleTest(TestCase):
    def setUp(self):
        ids = [900, 901, 902]
        users = [User(user_id=id_, facebook_id=id_) for id_ in ids]
        for user in users:
            user.save()

    def tearDown(self):
        ids = [900, 901, 902]
        users = [User.index.get(user_id=id_) for id_ in ids]
        for user in users:
            user.delete()


    def test_request(self):
        FriendshipManager.send_friendship_request(900, 902, "hey")
        FriendshipManager.send_friendship_request(901, 902, "hoy")

        # Check sent requests
        sent = FriendshipManager.get_sent_requests(900)
        self.assertEqual(len(sent), 1)

        sent = FriendshipManager.get_sent_requests(901)
        self.assertEqual(len(sent), 1)

        sent = FriendshipManager.get_sent_requests(902)
        self.assertEqual(len(sent), 0)


        # Check incoming requests.
        requests = FriendshipManager.get_incoming_requests(902)
        self.assertEqual(len(requests), 2)

        requests[0][0].accept()

        requests = FriendshipManager.get_incoming_requests(902)
        self.assertEqual(len(requests), 1)

        requests[0].accept()

        requests = FriendshipManager.get_incoming_requests(902)
        self.assertEqual(len(requests), 0)


    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
