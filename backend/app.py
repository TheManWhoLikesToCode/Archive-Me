from flask import Flask, jsonify, request, make_response
from flask_cors import cross_origin
from config import create_app
from celery import Celery
from blackboard_session_manager import BlackboardSessionManager
from tasks import login  # Assuming tasks are defined in tasks.py

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
bb_session_manager = BlackboardSessionManager()

@flask_app.post('/login')
@cross_origin()
def start_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    # Trigger Celery task
    task = login.delay(data['username'], data['password'])
    return jsonify({'message': 'Login in progress', 'task_id': task.id}), 202


@flask_app.get('/login/<task_id>')
@cross_origin()
def get_login_status(task_id):
    task = login.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({'message': 'Login in progress'}), 202
    elif task.state == 'SUCCESS':
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Login failed'}), 400

if __name__ == '__main__':
    flask_app.run(debug=True)