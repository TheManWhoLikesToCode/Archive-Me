import os
import time
import uuid
from behave import given, when, then
from blackboard_session import BlackboardSession
from blackboard_session_manager import BlackboardSessionManager
import assertpy
from behave import given, when, then
from blackboard_session import BlackboardSession
import os
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

#* Given steps
@given('a blackboard session manager')
def step_impl(context):
    context.manager = BlackboardSessionManager()


@given('an existing session for user "{username}"')
def step_impl(context, username):
    context.manager.get_bb_session(username)


@given('a blackboard session for user "{username}"')
def step_impl(context, username):
    context.manager.get_bb_session(username)
    context.temp_session = context.manager.retrieve_bb_session_by_username(
        username)


@given('inactive sessions older than {seconds:d} seconds')
def step_impl(context, seconds):
    context.blackboard_session_manager = BlackboardSessionManager()
    context.blackboard_session_manager.put_bb_session(
        'user1', BlackboardSession(str(uuid.uuid4()), time.time() - seconds - 1))


@given('no inactive sessions')
def step_impl(context):
    context.manager = BlackboardSessionManager()

    current_time = time.time()
    with context.manager.lock:
        inactive_sessions = [session_id for session_id, session in context.manager.bb_sessions.items()
                             if current_time - session.last_activity_time > 3600]  # 1 hour in seconds

        for session_id in inactive_sessions:
            username = next((user for user, id in context.manager.user_session_map.items(
            ) if id == session_id), None)
            if username:
                context.manager.delete_bb_session(username)


@given('an existing session with ID "{session_id}" for users "{user1}" and "{user2}"')
def step_impl(context, session_id, user1, user2):
    new_session = BlackboardSession(session_id, time.time())
    context.manager.bb_sessions[session_id] = new_session
    context.manager.user_session_map[user1] = session_id
    context.manager.user_session_map[user2] = session_id


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

#* When steps
@when('I request a session for user "{username}"')
def step_impl(context, username):
    context.session = context.manager.get_bb_session(username)


@when('I store the session for user "{username}"')
def step_impl(context, username):
    context.manager.put_bb_session(username, context.temp_session)


@when('I retrieve a session by session ID "{session_id}"')
def step_impl(context, session_id):
    context.session = context.manager.retrieve_bb_session_by_id(session_id)


@when('I retrieve a session by username "{username}"')
def step_impl(context, username):
    context.session = context.manager.retrieve_bb_session_by_username(username)


@when('I delete the session for user "{username}"')
def step_impl(context, username):
    context.initial_session_count = len(context.manager.bb_sessions)
    context.manager.delete_bb_session(username)


@when('I clean up inactive sessions')
def step_impl(context):
    context.initial_session_count = len(context.manager.bb_sessions)
    context.manager.clean_up_inactive_sessions()


@given('an existing session with ID "{session_id}"')
def step_impl(context, session_id):
    new_session = BlackboardSession(session_id, time.time())
    test_username = "test_user_for_" + session_id
    context.manager.bb_sessions[session_id] = new_session
    context.manager.user_session_map[test_username] = session_id


@when('I update the last activity time for "{username}"\'s session')
def step_impl(context, username):
    session = context.manager.retrieve_bb_session_by_username(username)
    session.last_activity_time = time.time()  # Update the last activity time


@when('I login')
def step_impl(context):
    context.session.login()
    context.response = context.session.get_response()


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


#* Then steps
@then('a new session should be created for "{username}"')
def step_impl(context, username):
    assertpy.assert_that(context.session).is_not_none()
    assertpy.assert_that(
        context.manager.user_session_map).contains_key(username)


@then('the existing session for "{username}" should be returned')
def step_impl(context, username):
    existing_session = context.manager.retrieve_bb_session_by_username(
        username)
    assertpy.assert_that(context.session).is_equal_to(existing_session)


@then('the session for "{username}" should be stored in the manager')
def step_impl(context, username):
    stored_session = context.manager.retrieve_bb_session_by_username(username)
    assertpy.assert_that(stored_session).is_equal_to(context.temp_session)


@then('the session with ID "{session_id}" should be returned')
def step_impl(context, session_id):
    assertpy.assert_that(context.session.session_id).is_equal_to(session_id)


@then('the session for "{username}" should be returned')
def step_impl(context, username):
    retrieved_session = context.manager.retrieve_bb_session_by_username(
        username)
    assertpy.assert_that(retrieved_session).is_not_none()
    assertpy.assert_that(retrieved_session).is_equal_to(context.session)


@then('the session for "{username}" should be removed')
def step_impl(context, username):
    assertpy.assert_that(
        context.manager.user_session_map).does_not_contain_key(username)


@then('all sessions older than {seconds:d} seconds should be removed')
def step_impl(context, seconds):
    current_time = time.time()
    for session in context.manager.bb_sessions.values():
        assertpy.assert_that(
            current_time - session.last_activity_time).is_less_than(seconds)


@then('no session should be returned')
def step_impl(context):
    assertpy.assert_that(context.session).is_none()


@then('no session should be removed')
def step_impl(context):
    final_session_count = len(context.manager.bb_sessions)
    assertpy.assert_that(final_session_count).is_equal_to(
        context.initial_session_count)


@then('the last activity time for "{username}"\'s session should be updated')
def step_impl(context, username):
    session = context.manager.retrieve_bb_session_by_username(username)
    current_time = time.time()
    tolerance = 1  # Define a tolerance for the time comparison

    assertpy.assert_that(session.last_activity_time).is_close_to(
        current_time, tolerance)


@then('the same session should be returned for both "{user1}" and "{user2}"')
def step_impl(context, user1, user2):
    session1 = context.manager.retrieve_bb_session_by_username(user1)
    session2 = context.manager.retrieve_bb_session_by_username(user2)
    assertpy.assert_that(session1).is_equal_to(session2)


@then('the response should be "Login successful."')
def step_impl(context):
    assert context.response == "Login successful."


@then('the response should be "The username you entered cannot be identified."')
def step_impl(context):
    assert context.response == "The username you entered cannot be identified."


@then('the response should be "Already logged in."')
def step_impl(context):
    assert context.response == "Already logged in."


@then('the enable instructors response should be "{message}"')
def step_impl(context, message):
    assert context.enable_instructors_response == message


@then('the get courses response should be "{message}"')
def step_impl(context, message):
    assert context.get_courses_response == message


@then('the get download tasks response should be "{message}"')
def step_impl(context, message):
    assert context.get_download_tasks_response == message
