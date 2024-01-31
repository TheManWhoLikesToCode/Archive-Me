from flask_cors import cross_origin
from config import create_app
from celery import Celery
from celery import shared_task
from flask import jsonify, make_response, request, abort
from blackboard_session_manager import BlackboardSessionManager
import os
from config import create_app


flask_app = create_app()
celery_app = flask_app.extensions["celery"]
bb_session_manager = BlackboardSessionManager()


@shared_task(name="scrape")
def scrape(username):
    try:
        bb_session = bb_session_manager.retrieve_bb_session(username)

        if not bb_session:
            return {'error': 'Session not found', 'status': 400}

        file_key = bb_session.scrape()
        if not bb_session.response:
            file_path = os.path.join(os.getcwd(), file_key)
            if not file_key or not os.path.isfile(file_path):
                return {'error': 'File not found', 'status': 404}

            return {'file_key': file_key, 'status': 200}
        else:
            return {'error': bb_session.response, 'status': 500}

    except Exception as e:
        return {'error': str(e), 'status': 500}



@shared_task(name="login_task")
def login(username, password):
    try:
        bb_session = bb_session_manager.get_bb_session(username)
        bb_session.username = username
        bb_session.password = password

        bb_session.login()
        response = bb_session.get_response()
        if response == 'Login successful.':
            bb_session_manager.put_bb_session(username, bb_session)
            return {'message': 'Logged in successfully', 'session_id': bb_session.session_id}
        elif response == 'Already logged in.':
            return {'message': 'Already logged in'}
        else:
            return {'error': response}, 401
    except Exception as e:
        return {'error': str(e)}, 500
    
@shared_task(name="is_logged_in")
@cross_origin(supports_credentials=True)
def is_logged_in():
    user_session = request.cookies.get('user_session')
    if user_session and bb_session_manager.retrieve_bb_session(user_session):
        return jsonify({'logged_in': True}), 200
    else:
        return jsonify({'logged_in': False}), 401