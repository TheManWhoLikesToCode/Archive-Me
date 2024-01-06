import logging
import random
import time
import unittest
from blackboard_scraper import BlackboardSession
from unittest.mock import MagicMock, patch
from usernames import usernames


class TestBlackboardSession(unittest.TestCase):

    # * Login Tests *#

    def test_valid_credentials_login(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)

        # Execute login
        session.login()

        response = session.get_response()

        # Check the response
        expected_message = "Login successful."

        self.assertEqual(response, expected_message)

    def test_invalid_both_login(self):
        # Set up
        username = 'InvalidUsername'
        password = 'InvalidPassword'
        session = BlackboardSession(username=username, password=password)

        # Execute login
        session.login()

        response = session.get_response()

        # Check the response
        expected_error_message = "The username you entered cannot be identified."

        self.assertEqual(response, expected_error_message)

    def test_failed_login_invalid_password(self):

        # selected a random username from usernames.py
        username = random.choice(list(usernames))

        invalid_password = 'InvalidPassword'
        session = BlackboardSession(
            username=username, password=invalid_password)

        # Execute login
        session.login()

        response = session.get_response()

        # Check the response
        error_messages = [
            "The password you entered was incorrect.", "Account has been disabled."
        ]

        self.assertTrue(response in error_messages)

    def test_failed_login_invalid_username(self):
        # Set up
        invalid_username = 'InvalidUsername'
        password = 'InvalidPassword'
        session = BlackboardSession(
            username=invalid_username, password=password)

        # Execute login
        session.login()

        response = session.get_response()

        # Check the response
        expected_error_message = "The username you entered cannot be identified."

        self.assertEqual(response, expected_error_message)

    # * Enable Instructors *#

    def test_enable_instructors_logged_in(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = True

        # Mock the GET request
        with patch.object(session, '_get_request') as mock_get_request:
            mock_get_request.return_value.status_code = 200
            mock_get_request.return_value.content = '''
                <html>
                    <form id="moduleEditForm">
                        <input type="hidden" value="nonce_value">
                    </form>
                </html>
            '''

            # Mock the POST request
            with patch.object(session, '_send_post_request') as mock_post_request:
                mock_post_request.return_value.status_code = 302
                mock_post_request.return_value.headers = {
                    'Location': 'https://kettering.blackboard.com'}

                # Execute enable_instructors
                session.enable_instructors()

                # Check the response
                self.assertTrue(session.instructorsFound)
                self.assertAlmostEqual(
                    session.last_activity_time, time.time(), delta=1)

    def test_enable_instructors_not_logged_in(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = False

        # Execute enable_instructors
        session.enable_instructors()

        # Check the response
        self.assertEqual(session.response, "Not logged in.")
        self.assertFalse(session.instructorsFound)
        self.assertIsNone(session.last_activity_time)

    def test_enable_instructors_get_request_failed(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = True

        # Mock the GET request
        with patch.object(session, '_get_request') as mock_get_request:
            mock_get_request.return_value.status_code = 500

            # Mock the logging.error function
            with patch('logging.error') as mock_logging_error:
                # Execute enable_instructors
                session.enable_instructors()

                # Check the response
                self.assertFalse(session.instructorsFound)

                # Check the logging.error call
                mock_logging_error.assert_called_once_with(
                    f"GET request failed with status code: {mock_get_request.return_value.status_code}")

    def test_enable_instructors_post_request_failed(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = True

        # Mock the GET request
        with patch.object(session, '_get_request') as mock_get_request:
            mock_get_request.return_value.status_code = 200
            mock_get_request.return_value.content = '''
                <html>
                    <form id="moduleEditForm">
                        <input type="hidden" value="nonce_value">
                    </form>
                </html>
            '''

            # Mock the POST request
            with patch.object(session, '_send_post_request') as mock_post_request:
                mock_post_request.return_value.status_code = 500

                # Mock the logging.error function
                with patch('logging.error') as mock_logging_error:
                    # Execute enable_instructors
                    session.enable_instructors()

                    # Check the response
                    self.assertFalse(session.instructorsFound)

                    # Check the logging.error call
                    mock_logging_error.assert_called_once_with(
                        f"POST request failed with status code: {mock_post_request.return_value.status_code}")


if __name__ == '__main__':
    unittest.main()
