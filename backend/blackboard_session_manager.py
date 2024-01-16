import uuid
from blackboard_session import BlackboardSession

class BlackboardSessionManager:
    def __init__(self):
        self.bb_sessions = {}
        self.user_session_map = {}

    def get_bb_session(self, username):
        if username not in self.user_session_map:
            session_id = str(uuid.uuid4())  # Generate a unique session ID
            self.user_session_map[username] = session_id
            # Store the session object
            self.bb_sessions[session_id] = BlackboardSession()

        return self.bb_sessions[self.user_session_map[username]]

    def put_bb_session(self, username, bb_session):
        session_id = self.user_session_map.get(username)
        if session_id:
            self.bb_sessions[session_id] = bb_session

    def retrieve_bb_session(self, username):
        session_id = self.user_session_map.get(username)
        if session_id:
            return self.bb_sessions.get(session_id)

        return None

    def delete_bb_session(self, username):
        session_id = self.user_session_map.get(username)
        if session_id:
            session_to_delete = self.bb_sessions.pop(session_id, None)
            if session_to_delete:
                del self.user_session_map[username]
