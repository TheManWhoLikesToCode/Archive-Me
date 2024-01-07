import random
import time
import unittest
from blackboard_scraper import BlackboardSession
from unittest.mock import patch
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

    """     
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
    """

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

    # * Get Courses *#

    def test_get_courses_logged_in(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
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
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = False

        # Execute get_courses
        session.get_courses()

        # Check the response
        self.assertEqual(session.response, "Not logged in.")
        self.assertEqual(session.courses, {})
        self.assertIsNone(session.last_activity_time)

    def test_get_courses_no_courses(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
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
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
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

    # * Get Download Tasks *#

def test_get_download_tasks_logged_in(self):
    # Set up
    username = 'Free8864'
    password = '#CFi^F6TTwot2j'
    session = BlackboardSession(username=username, password=password)
    session.is_logged_in = True
    session.courses = {
        'Course 1': 'course1_link',
        'Course 2': 'course2_link'
    }

    with patch.object(session, '_get_request') as mock_get_request:
        mock_get_request.side_effect = [
            type('', (), {'status_code': 200, 'content': '''
                <html>
                    <body>
                        <div id="containerdiv">
                            <ul>
                                <li>
                                    <a href="/course1_link/assignment1">Assignment 1</a>
                                    <div class="details">
                                        <a href="download_link1">Download</a>
                                    </div>
                                </li>
                                <li>
                                    <a href="/course1_link/assignment2">Assignment 2</a>
                                    <div class="details">
                                        <a href="download_link2">Download</a>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </body>
                </html>
            '''}),
            type('', (), {'status_code': 200, 'content': '''
                <html>
                    <body>
                        <div id="containerdiv">
                            <ul>
                                <li>
                                    <a href="/course2_link/assignment1">Assignment 1</a>
                                    <div class="details">
                                        <a href="download_link1">Download</a>
                                    </div>
                                </li>
                                <li>
                                    <a href="/course2_link/assignment2">Assignment 2</a>
                                    <div class="details">
                                        <a href="download_link2">Download</a>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </body>
                </html>
            '''})
        ]

        # Call the method
        session.get_download_tasks()

        # Assert the result
        expected_result = [
            ('Course 1', 'Assignment 1', 'download_link1'),
            ('Course 1', 'Assignment 2', 'download_link2'),
            ('Course 2', 'Assignment 1', 'download_link1'),
            ('Course 2', 'Assignment 2', 'download_link2'),
        ]

        self.assertEqual(session.download_tasks, expected_result)
        self.assertTrue(session.downloadTasksFound)
        self.assertAlmostEqual(
            session.last_activity_time, time.time(), delta=1)


    def test_get_download_tasks_not_logged_in(self):
        # Set up
        username = 'Free8864'
        password = '#CFi^F6TTwot2j'
        session = BlackboardSession(username=username, password=password)
        session.is_logged_in = False

        # Execute get_download_tasks
        session.get_download_tasks()

        # Check the response
        self.assertEqual(session.response, "Not logged in.")
        self.assertFalse(session.downloadTasksFound)
        self.assertIsNone(session.last_activity_time)


if __name__ == '__main__':
    unittest.main()
