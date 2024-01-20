import uuid
import threading
import time
from blackboard_session import BlackboardSession


class BlackboardSessionManager:
    def __init__(self):
        self.bb_sessions = {}
        self.user_session_map = {}
        self.lock = threading.Lock()

    def get_bb_session(self, username):
        with self.lock:
            if username not in self.user_session_map:
                session_id = str(uuid.uuid4())  # Generate a unique session ID
                self.user_session_map[username] = session_id
                # Store the session object
                self.bb_sessions[session_id] = BlackboardSession(
                    session_id, time.time())

            return self.bb_sessions[self.user_session_map[username]]

    def put_bb_session(self, username, bb_session):
        with self.lock:
            session_id = self.user_session_map.get(username)
            if session_id:
                self.bb_sessions[session_id] = bb_session

    def retrieve_bb_session_by_username(self, username):
        with self.lock:
            session_id = self.user_session_map.get(username)
            if session_id:
                return self.bb_sessions.get(session_id)
        return None

    def retrieve_bb_session_by_id(self, session_id):
        with self.lock:
            return self.bb_sessions.get(session_id)

    def retrieve_bb_session(self, identifier):
        if isinstance(identifier, str) and '-' in identifier:
            return self.retrieve_bb_session_by_id(identifier)
        else:
            return self.retrieve_bb_session_by_username(identifier)

    def delete_bb_session(self, username):
        with self.lock:
            session_id = self.user_session_map.pop(username, None)
            if session_id:
                return self.bb_sessions.pop(session_id, None)

    def clean_up_inactive_sessions(self, inactivity_threshold_seconds=3600):
        with self.lock:
            current_time = time.time()
            inactive_sessions = [username for username, session_id in self.user_session_map.items()
                                 if current_time - self.bb_sessions[session_id].last_activity_time > inactivity_threshold_seconds]
            for username in inactive_sessions:
                self.delete_bb_session(username)
