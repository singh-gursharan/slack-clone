from flask_login import current_user
from flask import json, jsonify, send_from_directory
from app.auth.forms import User
from app import celery, create_app
import time


@celery.task(bind=True)
def get_all_post(self, id):
    app = create_app()
    with app.app_context():
        user = User.query.get(id)
        posts = user.posts.all()
        postsdata = []
        eachpostdata = {}
        length = len(posts)
        i = 0

        for post in posts:
            eachpostdata['timestamp'] = post.timestamp
            eachpostdata['body'] = post.body
            eachpostdata['in_channel'] = post.in_channel.name
            postsdata = postsdata + [eachpostdata]
            self.update_state(state='PROGRESS', meta={'current': i, 'total': length,
                                                      'status': post.in_channel.name})
            i = i+1
            time.sleep(0.1)

    f = open("app/postsdata.json", "w+")
    json.dump(postsdata, f, indent=4, ensure_ascii=False)
    f.close()

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': True}
