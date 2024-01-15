import argparse
import os
import random
import time
import unittest

from dotenv import load_dotenv
from blackboard_scraper import BlackboardSession
from unittest.mock import patch
from usernames import usernames

""""
Test Case Senarios:

#* Login *#

- Valid credentials
- Invalid username
- Invalid password
- Invalid username and password

# TODO:

- Failed GET request
- Failed POST request
- HTML parsing failed

#* Enable Instructors *#

- Logged in
- Not logged in
- GET request failed
- POST request failed

# TODO:

- HTML parsing failed
- No instructors found
- Instructors found

#* Get Courses *#

- Logged in
- Not logged in
- No courses
- Error finding course list

# TODO:

- HTML parsing failed

#* Get Download Tasks *#

- Logged in
- Not logged in

# TODO:

- HTML parsing failed

"""


class TestBlackboardSession(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.username = os.environ.get('TEST_USERNAME')
        self.password = os.environ.get('TEST_PASSWORD')

    # * Login Tests *#

    def test_valid_credentials_login(self):

        session = BlackboardSession(
            username=self.username, password=self.password)

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
        session = BlackboardSession()
        session.is_logged_in = True

        # Mock the GET request
        with patch.object(session, '_get_request') as mock_get_request:
            mock_get_request.return_value.status_code = 200
            mock_get_request.return_value.content = '''
            <html>
                <body>
                    <form id="moduleEditForm">
                        <input type="hidden" value="fake_nonce_value">
                    </form>
                    <table id="blockAttributes_table_jsListFULL_Student_1_1_body">
                        <tr id="FULL_Student_1_1_row:_123_456"></tr>
                        <tr id="FULL_Student_1_1_row:_789_101"></tr>
                    </table>
                </body>
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
        session = BlackboardSession()
        session.is_logged_in = False

        # Execute enable_instructors
        session.enable_instructors()

        # Check the response
        self.assertEqual(session.response, "Not logged in.")
        self.assertFalse(session.instructorsFound)
        self.assertIsNone(session.last_activity_time)

    def test_enable_instructors_get_request_failed(self):

        # Set up
        session = BlackboardSession()
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
                    "An error occurred enabling instructors: GET request failed."
                )

    def test_enable_instructors_post_request_failed(self):

        # Set up
        session = BlackboardSession()
        session.is_logged_in = True

        # Mock the GET request
        with patch.object(session, '_get_request') as mock_get_request:
            mock_get_request.return_value.status_code = 200
            mock_get_request.return_value.content = '''
                <html>
                    <body>
                        <form id="moduleEditForm">
                            <input type="hidden" value="fake_nonce_value">
                        </form>
                        <table id="blockAttributes_table_jsListFULL_Student_1_1_body">
                            <tr id="FULL_Student_1_1_row:_123_456"></tr>
                            <tr id="FULL_Student_1_1_row:_789_101"></tr>
                        </table>
                    </body>
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
                        "An error occurred enabling instructors: POST request failed."
                    )

    # * Get Courses *#

    def test_get_courses_logged_in(self):
        # Set up
        session = BlackboardSession()

        session.is_logged_in = True

        # Mock the POST request
        with patch.object(session, '_send_post_request') as mock_post_request:
            mock_post_request.return_value.status_code = 200
            mock_post_request.return_value.content = '''
                <html>
                    <div id="_4_1termCourses__254_1">
                        <ul>
                            <li><a href="course1_link">Course 1</a></li>
                            <li><a href="course2_link">Course 2</a></li>
                        </ul>
                    </div>
                </html>
            '''

            # Execute get_courses
            session.get_courses()

            # Check the response
            expected_courses = {
                'Course 1': 'course1_link',
                'Course 2': 'course2_link'
            }
            self.assertEqual(session.courses, expected_courses)
            self.assertAlmostEqual(
                session.last_activity_time, time.time(), delta=1)

    def test_get_courses_not_logged_in(self):

        # Set up
        session = BlackboardSession()
        session.is_logged_in = False

        # Execute get_courses
        session.get_courses()

        # Check the response
        self.assertEqual(session.response, "Not logged in.")
        self.assertEqual(session.courses, {})
        self.assertIsNone(session.last_activity_time)

    def test_get_courses_no_courses(self):
        # Set up
        session = BlackboardSession()

        session.is_logged_in = True

        # Mock the POST request
        with patch.object(session, '_send_post_request') as mock_post_request:
            mock_post_request.return_value.status_code = 200
            mock_post_request.return_value.content = '''
                <html>
                    <div id="_4_1termCourses__254_1">
                        <ul>
                            <li>You are not currently enrolled in any courses.</li>
                        </ul>
                    </div>
                </html>
            '''

            # Execute get_courses
            session.get_courses()

            # Check the response
            self.assertEqual(session.response,
                             "You are not currently enrolled in any courses.")
            self.assertEqual(session.courses, {})

    def test_get_courses_error_finding_course_list(self):
        # Set up
        session = BlackboardSession()

        session.is_logged_in = True

        # Mock the POST request
        with patch.object(session, '_send_post_request') as mock_post_request:
            mock_post_request.return_value.status_code = 500

            # Mock the logging.error function
            with patch('logging.error') as mock_logging_error:
                # Execute get_courses
                session.get_courses()

                # Check the response
                self.assertIsInstance(session.response, Exception)
                self.assertEqual(str(session.response), 'POST request failed.')
                self.assertEqual(session.courses, {})
                mock_logging_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
