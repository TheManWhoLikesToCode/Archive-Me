import os
import random
import time
import pytest
from dotenv import load_dotenv
from blackboard_scraper import BlackboardSession
from unittest.mock import MagicMock, patch
from usernames import usernames



load_dotenv()

import os
import random
import time
import unittest

from dotenv import load_dotenv
from blackboard_scraper import BlackboardSession
from unittest.mock import MagicMock, patch
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

@pytest.fixture
def session():
    username = os.getenv('TEST_USERNAME')
    password = os.getenv('TEST_PASSWORD')
    return BlackboardSession(username=username, password=password)


@pytest.fixture
def random_username():
    return random.choice(list(usernames))


def test_valid_credentials_login(session):
    session.login()
    response = session.get_response()
    expected_message = "Login successful."
    assert response == expected_message


def test_invalid_both_login():
    session = BlackboardSession(
        username='InvalidUsername', password='InvalidPassword')
    session.login()
    response = session.get_response()
    expected_error_message = "The username you entered cannot be identified."
    assert response == expected_error_message


def test_failed_login_invalid_password(random_username):
    session = BlackboardSession(
        username=random_username, password='InvalidPassword')
    session.login()
    response = session.get_response()
    error_messages = [
        "The password you entered was incorrect.", "Account has been disabled."]
    assert response in error_messages


def test_failed_login_invalid_username():
    session = BlackboardSession(
        username='InvalidUsername', password='InvalidPassword')
    session.login()
    response = session.get_response()
    expected_error_message = "The username you entered cannot be identified."
    assert response == expected_error_message


@pytest.fixture
def mock_session():
    session = BlackboardSession()
    session.is_logged_in = True
    return session


def test_enable_instructors_logged_in(mock_session):
    with patch.object(mock_session, '_get_request') as mock_get_request, \
            patch.object(mock_session, '_send_post_request') as mock_post_request:
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
        mock_post_request.return_value.status_code = 302
        mock_post_request.return_value.headers = {
            'Location': 'https://kettering.blackboard.com'}
        mock_session.enable_instructors()
        assert mock_session.instructorsFound
        assert abs(mock_session.last_activity_time - time.time()) < 1


def test_enable_instructors_not_logged_in():
    session = BlackboardSession()
    session.is_logged_in = False
    session.enable_instructors()
    assert session.response == "Not logged in."
    assert not session.instructorsFound
    assert session.last_activity_time is None


def test_enable_instructors_get_request_failed(mock_session):
    with patch.object(mock_session, '_get_request') as mock_get_request, \
            patch('logging.error') as mock_logging_error:
        mock_get_request.return_value.status_code = 500
        mock_session.enable_instructors()
        assert not mock_session.instructorsFound
        mock_logging_error.assert_called_once()


def test_enable_instructors_post_request_failed(mock_session):
    with patch.object(mock_session, '_get_request') as mock_get_request, \
            patch.object(mock_session, '_send_post_request') as mock_post_request, \
            patch('logging.error') as mock_logging_error:
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
        mock_post_request.return_value.status_code = 500
        mock_session.enable_instructors()
        assert not mock_session.instructorsFound
        mock_logging_error.assert_called_once()


def test_get_courses_logged_in(mock_session):
    with patch.object(mock_session, '_send_post_request') as mock_post_request:
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
        mock_session.get_courses()
        expected_courses = {'Course 1': 'course1_link',
                            'Course 2': 'course2_link'}
        assert mock_session.courses == expected_courses
        assert abs(mock_session.last_activity_time - time.time()) < 1


def test_get_courses_not_logged_in():
    session = BlackboardSession()
    session.is_logged_in = False
    session.get_courses()
    assert session.response == "Not logged in."
    assert session.courses == {}
    assert session.last_activity_time is None


def test_get_courses_no_courses(mock_session):
    with patch.object(mock_session, '_send_post_request') as mock_post_request:
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
        mock_session.get_courses()
        assert mock_session.response == "You are not currently enrolled in any courses."
        assert mock_session.courses == {}


def test_get_courses_error_finding_course_list(mock_session):
    with patch.object(mock_session, '_send_post_request') as mock_post_request, \
            patch('logging.error') as mock_logging_error:
        mock_post_request.return_value.status_code = 500
        mock_session.get_courses()
        assert isinstance(mock_session.response, Exception)
        assert str(mock_session.response) == 'POST request failed.'
        assert mock_session.courses == {}
        mock_logging_error.assert_called_once()


def test_get_download_tasks_logged_in(mock_session):
    with patch.object(mock_session, 'get_download_tasks') as mock_get_download_tasks:
        mock_session.is_logged_in = True
        mock_session.get_download_tasks()
        mock_get_download_tasks.assert_called_once()


def test_get_download_tasks_not_logged_in():
    session = BlackboardSession()
    session.is_logged_in = False
    with patch.object(session, 'get_download_tasks') as mock_get_download_tasks:
        session.get_download_tasks()

        # Running the tests
        assert session.download_tasks == []
        assert session.downloadTasksFound == False
        assert session.last_activity_time == None


if __name__ == "__main__":
    pytest.main()
