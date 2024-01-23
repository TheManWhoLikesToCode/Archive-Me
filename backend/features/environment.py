from app import app

def before_all(context):
    context.client = app.test_client()