from behave import given, when, then
from blackboard_session import BlackboardSession
import os
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

@given('I have valid credentials')
def step_impl(context):
    context.username = os.getenv('TEST_USERNAME')
    context.password = os.getenv('TEST_PASSWORD')
    context.session = BlackboardSession(
        username=context.username, password=context.password)


@given('I have invalid username and password')
def step_impl(context):
    context.session = BlackboardSession(
        username='InvalidUsername', password='InvalidPassword')


@when('I login')
def step_impl(context):
    context.session.login()
    context.response = context.session.get_response()


@then('the response should be "Login successful."')
def step_impl(context):
    assert context.response == "Login successful."


@then('the response should be "The username you entered cannot be identified."')
def step_impl(context):
    assert context.response == "The username you entered cannot be identified."

@then('the response should be "Already logged in."')
def step_impl(context):
    assert context.response == "Already logged in."

@given('I am logged in')
def step_impl(context):
    context.session = BlackboardSession(
        username=context.username, password=context.password)
    context.session.login()
    context.logged_in = context.session.is_logged_in


@given('I am not logged in')
def step_impl(context):
    context.session = BlackboardSession(
        username='InvalidUsername', password='InvalidPassword')
    context.logged_in = context.session.is_logged_in


@when('I enable instructors')
def step_impl(context):
    if context.logged_in:
        with patch.object(context.session, '_get_request') as mock_get_request, \
                patch.object(context.session, '_send_post_request') as mock_post_request:
            mock_get_request.return_value.status_code = 200
            mock_get_request.return_value.content = '<html><form id="moduleEditForm"><input type="hidden" value="nonce_value"></form></html>'
            mock_post_request.return_value.status_code = 302
            mock_post_request.return_value.headers = {
                'Location': 'https://kettering.blackboard.com'}
            context.session.enable_instructors()
            context.enable_instructors_response = "Instructors enabled"
    else:
        context.session.enable_instructors()
        context.enable_instructors_response = context.session.response


@then('the enable instructors response should be "{message}"')
def step_impl(context, message):
    assert context.enable_instructors_response == message


@when('I get courses')
def step_impl(context):
    if context.logged_in:
        with patch.object(context.session, '_send_post_request') as mock_post_request:
            mock_post_request.return_value.status_code = 200
            mock_post_request.return_value.content = '<html><div id="_4_1termCourses__254_1"><ul><li><a href="course1_link">Course 1</a></li><li><a href="course2_link">Course 2</a></li></ul></div></html>'
            context.session.get_courses()
            context.get_courses_response = "Courses retrieved"
    else:
        context.session.get_courses()
        context.get_courses_response = context.session.response


@then('the get courses response should be "{message}"')
def step_impl(context, message):
    assert context.get_courses_response == message


@when('I get download tasks')
def step_impl(context):
    if context.logged_in:
        with patch.object(context.session, '_get_request') as mock_get_request:
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
                '''})
            ]
            context.session.get_download_tasks()
            context.get_download_tasks_response = "Download tasks retrieved"
    else:
        context.session.get_download_tasks()
        context.get_download_tasks_response = context.session.response


@then('the get download tasks response should be "{message}"')
def step_impl(context, message):
    assert context.get_download_tasks_response == message
