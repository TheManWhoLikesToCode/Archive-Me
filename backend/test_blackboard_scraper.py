import argparse
import os
import random
import time
import unittest

from dotenv import load_dotenv
from blackboard_session import BlackboardSession
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
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Course and Term Management</title>
                </head>
                <body>
                    <form method="post" action="tabAction?tab_tab_group_id=_1_1&amp;forwardUrl=proc_edit/_4_1/bbcourseorg&amp;recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1" id="moduleEditForm">
                        <input type="hidden" name="blackboard.platform.security.NonceUtil.nonce" value="3355f352-678e-4821-bd3d-a6f548fd7cf9">
                        <input type="hidden" name="cmd" id="cmd" value="processEdit">
                        <input type="hidden" name="serviceLevel" id="serviceLevel" value="">

                        <!-- Course Table -->
                        <table id="blockAttributes_table_jsListFULL_Student_35314_1">
                            <!-- Table Headers (simplified for brevity) -->
                            <thead>
                                <tr>
                                    <th>Course</th>
                                    <th>Course Name</th>
                                    <th>Course ID</th>
                                    <th>Instructors</th>
                                </tr>
                            </thead>
                            <tbody id="blockAttributes_table_jsListFULL_Student_35314_1_body">
                                <!-- Course Rows -->
                                <tr id="blockAttributes_table_jsListFULL_Student_35314_1_row:_52268_1">
                                    <td align="LEFT" class="" id="miniListElement-showcoursename:row_0">
                                        <input id="amc.showcourse._52268_1" type="checkbox" value="true" name="amc.showcourse._52268_1" checked="checked">
                                    </td>
                                    <td align="LEFT" class="" id="miniListElement-showcourseid:row_0">
                                        <input id="amc.showcourseid._52268_1" type="checkbox" value="true" name="amc.showcourseid._52268_1" checked="checked">
                                    </td>
                                    <td align="LEFT" class="" id="miniListElement-showinstructors:row_0">
                                        <input id="amc.showinstructors._52268_1" type="checkbox" value="true" name="amc.showinstructors._52268_1" checked="checked">
                                    </td>
                                </tr>
                                <!-- Additional course rows can be added here -->
                            </tbody>
                        </table>

                        <!-- Term Table -->
                        <table id="termDisplay_table_jsListTermDisplay">
                            <!-- Table Headers (simplified for brevity) -->
                            <thead>
                                <tr>
                                    <th>Term Name</th>
                                    <th>Term Duration</th>
                                    <th>Show Term</th>
                                    <th>Expand Term</th>
                                </tr>
                            </thead>
                            <tbody id="termDisplay_table_jsListTermDisplay_body">
                                <!-- Term Rows -->
                                <tr id="termDisplay_table_jsListTermDisplay_row:_243_1">
                                    <td align="LEFT" class="" id="miniListElement-showterm:row_0">
                                        <input id="amc.showterm._243_1" type="checkbox" value="true" name="amc.showterm._243_1" checked="checked">
                                    </td>
                                    <td align="LEFT" class="" id="miniListElement-expandterm:row_0">
                                        <input id="termCourses__243_1" type="checkbox" value="true" name="termCourses__243_1" checked="checked">
                                    </td>
                                </tr>
                                <!-- Additional term rows can be added here -->
                            </tbody>
                        </table>

                        <!-- Submit Button -->
                        <input id="bottom_Submit" class="submit button-1" name="bottom_Submit" type="submit" value="Submit">
                    </form>
                </body>
                </html>

            '''

            # Mock the POST request
            with patch.object(session, '_send_post_request') as mock_post_request:
                mock_post_request.return_value.status_code = 302
                mock_post_request.return_value.headers = {
                    'Location': 'https://kettering.blackboard.com'}

                # Execute enable_instructors
                session.enable_instructors_and_year_season()

                # Check the response
                self.assertTrue(session.instructorsFound)
                self.assertAlmostEqual(
                    session.last_activity_time, time.time(), delta=1)

    def test_enable_instructors_not_logged_in(self):

        # Set up
        session = BlackboardSession()
        session.is_logged_in = False

        # Execute enable_instructors
        session.enable_instructors_and_year_season()

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
                session.enable_instructors_and_year_season()

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
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Course and Term Management</title>
            </head>
            <body>
                <form method="post" action="tabAction?tab_tab_group_id=_1_1&amp;forwardUrl=proc_edit/_4_1/bbcourseorg&amp;recallUrl=%2Fwebapps%2Fportal%2Fexecute%2Ftabs%2FtabAction%3Ftab_tab_group_id%3D_1_1" id="moduleEditForm">
                    <input type="hidden" name="blackboard.platform.security.NonceUtil.nonce" value="3355f352-678e-4821-bd3d-a6f548fd7cf9">
                    <input type="hidden" name="cmd" id="cmd" value="processEdit">
                    <input type="hidden" name="serviceLevel" id="serviceLevel" value="">

                    <!-- Course Table -->
                    <table id="blockAttributes_table_jsListFULL_Student_35314_1">
                        <!-- Table Headers (simplified for brevity) -->
                        <thead>
                            <tr>
                                <th>Course</th>
                                <th>Course Name</th>
                                <th>Course ID</th>
                                <th>Instructors</th>
                            </tr>
                        </thead>
                        <tbody id="blockAttributes_table_jsListFULL_Student_35314_1_body">
                            <!-- Course Rows -->
                            <tr id="blockAttributes_table_jsListFULL_Student_35314_1_row:_52268_1">
                                <td align="LEFT" class="" id="miniListElement-showcoursename:row_0">
                                    <input id="amc.showcourse._52268_1" type="checkbox" value="true" name="amc.showcourse._52268_1" checked="checked">
                                </td>
                                <td align="LEFT" class="" id="miniListElement-showcourseid:row_0">
                                    <input id="amc.showcourseid._52268_1" type="checkbox" value="true" name="amc.showcourseid._52268_1" checked="checked">
                                </td>
                                <td align="LEFT" class="" id="miniListElement-showinstructors:row_0">
                                    <input id="amc.showinstructors._52268_1" type="checkbox" value="true" name="amc.showinstructors._52268_1" checked="checked">
                                </td>
                            </tr>
                            <!-- Additional course rows can be added here -->
                        </tbody>
                    </table>

                    <!-- Term Table -->
                    <table id="termDisplay_table_jsListTermDisplay">
                        <!-- Table Headers (simplified for brevity) -->
                        <thead>
                            <tr>
                                <th>Term Name</th>
                                <th>Term Duration</th>
                                <th>Show Term</th>
                                <th>Expand Term</th>
                            </tr>
                        </thead>
                        <tbody id="termDisplay_table_jsListTermDisplay_body">
                            <!-- Term Rows -->
                            <tr id="termDisplay_table_jsListTermDisplay_row:_243_1">
                                <td align="LEFT" class="" id="miniListElement-showterm:row_0">
                                    <input id="amc.showterm._243_1" type="checkbox" value="true" name="amc.showterm._243_1" checked="checked">
                                </td>
                                <td align="LEFT" class="" id="miniListElement-expandterm:row_0">
                                    <input id="termCourses__243_1" type="checkbox" value="true" name="termCourses__243_1" checked="checked">
                                </td>
                            </tr>
                            <!-- Additional term rows can be added here -->
                        </tbody>
                    </table>

                    <!-- Submit Button -->
                    <input id="bottom_Submit" class="submit button-1" name="bottom_Submit" type="submit" value="Submit">
                </form>
            </body>
            </html>

            '''

            # Mock the POST request
            with patch.object(session, '_send_post_request') as mock_post_request:
                mock_post_request.return_value.status_code = 500

                # Mock the logging.error function
                with patch('logging.error') as mock_logging_error:
                    # Execute enable_instructors
                    session.enable_instructors_and_year_season()

                    # Check the response
                    self.assertFalse(session.instructorsFound)

                    # Check the logging.error call
                    mock_logging_error.assert_called_once_with(
                        "An error occurred enabling instructors: POST request failed."
                    )

    # * Get Courses *#

    def test_get_courses_with_instructors_logged_in(self):
        # Set up
        session = BlackboardSession()
        session.is_logged_in = True
        session.instructorsFound = True

        # Mock the POST request
        with patch.object(session, '_send_post_request') as mock_post_request:
            mock_post_request.return_value.status_code = 200
            mock_post_request.return_value.content = '''
                <html>
                    <div id="div_4_1">
                        <div class="noItems" style="display:none">All of your courses are hidden.</div>

                        <h3 class="termHeading-coursefakeclass" id="anonymous_element_7">
                            <a id="afor_4_1termCourses__243_1" title="Collapse" href="#" class="itemHead itemHeadOpen"
                                onclick="toggleTermLink('_4_1','termCourses__243_1', 'ebd88f5b-786d-4517-9ea5-cb227d799d4e')">
                                <span class="hideoff">Collapse</span>
                                Summer 2023</a>
                        </h3>
                        <div id="_4_1termCourses__243_1" style="">
                            <h4 class="u_indent" id="anonymous_element_8">Courses where you are: Student</h4>
                            <ul class="portletList-img courseListing coursefakeclass u_indent">
                                <li>
                                    <img alt=""
                                        src="https://learn.content.blackboardcdn.com/3900.82.0-rel.45+82d6e90/images/ci/icons/bookopen_li.gif"
                                        width="12" height="12">
                                    <a href=" /webapps/blackboard/execute/launcher?type=Course&amp;id=_51316_1&amp;url="
                                        target="_top">35221.202303: Culminating Undergraduate Experience: Thesis (CILE-400-01) Summer
                                        2023</a>
                                    <div class="courseInformation">
                                        <span class="courseRole">
                                            Instructor:
                                        </span>
                                        <span class="name">Michelle Gebhardt;&nbsp;&nbsp;</span>
                                    </div>
                                </li>
                            </ul>
                        </div>
                        <h3 class="termHeading-coursefakeclass" id="anonymous_element_9">
                            <a id="afor_4_1termCourses__259_1" title="Collapse" href="#" class="termToggleLink itemHead itemHeadOpen"
                                onclick="toggleTermLink('_4_1','termCourses__259_1', 'ebd88f5b-786d-4517-9ea5-cb227d799d4e')">
                                <span class="hideoff">Collapse</span>
                                Winter 2024</a>
                        </h3>
                        <div id="_4_1termCourses__259_1" style="">
                            <h4 class="u_indent" id="anonymous_element_10">Courses where you are: Student</h4>
                            <ul class="portletList-img courseListing coursefakeclass u_indent">
                                <li>
                                    <img alt=""
                                        src="https://learn.content.blackboardcdn.com/3900.82.0-rel.45+82d6e90/images/ci/icons/bookopen_li.gif"
                                        width="12" height="12">
                                    <a href=" /webapps/blackboard/execute/launcher?type=Course&amp;id=_52268_1&amp;url="
                                        target="_top">15664.202401: COOP-002-01: Co-op Educat Exp - Employed - WINTER</a>
                                    <div class="courseInformation">
                                        <span class="courseRole">
                                            Instructor:
                                        </span>
                                        <span class="noItems">
                                            No Instructors.
                                        </span>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </html>
            '''

            # Execute get_courses
            session.get_courses()

            # Check the response
            expected_courses = {
                'CILE-400-01, Gebhardt, Summer 2023': '/webapps/blackboard/execute/launcher?type=Course&id=_51316_1&url=',
                'COOP-002-01, No Instructor, Winter 2024': '/webapps/blackboard/execute/launcher?type=Course&id=_52268_1&url='
            }
            self.assertEqual(session.courses, expected_courses)
            self.assertAlmostEqual(
                session.last_activity_time, time.time(), delta=1)

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
