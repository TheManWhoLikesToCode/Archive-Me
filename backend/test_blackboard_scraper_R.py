import logging
import random
import unittest
from blackboard_scraper_R import BlackboardSession
from unittest.mock import MagicMock, patch
from usernames import usernames

class TestBlackboardSession(unittest.TestCase):

    def test_valid_credentials_login(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)

        # Execute login
        response = session.login()

        # Check the response
        expected_message = "Login successful."

        self.assertEqual(response, expected_message)


    def test_invalid_both_login(self):
        # Set up
        username = 'InvalidUsername'
        password = 'InvalidPassword'
        session = BlackboardSession(username=username, password=password)

        # Execute login
        response = session.login()

        # Check the response
        expected_error_message = "The username you entered cannot be identified."

        self.assertEqual(response, expected_error_message)


    def test_failed_login_invalid_password(self):

        # selected a random username from usernames.py
        username = random.choice(list(usernames))

        invalid_password = 'InvalidPassword'
        session = BlackboardSession(username=username, password=invalid_password)

        # Execute login
        response = session.login()

        # Check the response
        error_messages = [
            "The password you entered was incorrect.", "Account has been disabled."
        ]

        self.assertTrue(response in error_messages)


    def test_failed_login_invalid_username(self):
        # Set up
        invalid_username = 'InvalidUsername'
        password = 'InvalidPassword'
        session = BlackboardSession(username=invalid_username, password=password)

        # Execute login
        response = session.login()

        # Check the response
        expected_error_message = "The username you entered cannot be identified."

        self.assertEqual(response, expected_error_message)


if __name__ == '__main__':
    unittest.main()
