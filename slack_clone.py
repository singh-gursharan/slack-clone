from app import db, create_app
from app.models import Channel, Post, User


slack_app_instance = create_app()

@slack_app_instance.shell_context_processor
def make_shell_context():
    return {'Channel': Channel, 'User': User, 'Post': Post, 'db': db}