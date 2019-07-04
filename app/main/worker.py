from flask_login import current_user
from flask import json, jsonify, send_from_directory
from app.auth.forms import User
from app import celery, create_app
import time


@celery.task(bind=True)
def get_all_posts(self, user_id):
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': 1,
                                                      'status': ''})
    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        posts = user.posts.all()
        postsdata = []
        eachpostdata = {}
        length = len(posts)
        i = 0
        for post in posts:
            eachpostdata = {
                'timestamp': post.timestamp,
                'body': post.body,
                'in_channel': post.in_channel.name
            }
            postsdata.append(eachpostdata)
            self.update_state(state='PROGRESS', meta={'current': i, 'total': length,
                                                      'status': post.in_channel.name})
            i = i+1
        with open(f"app/postsdata_{user_id}.json", "w+") as f:
            json.dump(postsdata, f, indent=4, ensure_ascii=False)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': True}
