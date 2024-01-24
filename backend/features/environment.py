from app import app

def before_all(context):
    context.client = app.test_client()

def after_scenario(context, scenario):
    context.client.post('/logout')
