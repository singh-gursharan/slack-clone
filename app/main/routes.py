from flask import render_template, redirect, send_file, url_for, jsonify, json, request, g, send_from_directory, current_app, flash
from flask_babel import get_locale
from flask_login import current_user
from app.main import bp
from flask_login import login_required
from app.main.forms import PostForm, CreateChannelForm, SearchForm
from app.models import Channel, Post, User
from app import db
from dateutil.parser import parse
from datetime import datetime
from app import celery
from app.main.worker import get_all_post


@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    channels = Channel.query.all()
    return render_template("index.html", title='Home page', channels=channels)


@bp.route('/index/<channel_id>', methods=['GET', 'POST'])
@login_required
def index_with_channel(channel_id):
    message_form = PostForm()
    channel = Channel.query.filter_by(id=channel_id).first()
    if message_form.validate_on_submit():
        post = Post(body=message_form.post.data,
                    author=current_user, in_channel=channel)
        db.session.add(post)
        db.session.commit()
        post_response = {
            'username': current_user.username,
            'img_url': post.author.avatar(70),
            'timestamp': post.timestamp,
            'utctimestr': str(post.timestamp)
        }
        # return redirect(url_for('main.index_with_channel', channel_id=channel_id))
        json.dumps(post_response)
        return jsonify(post_response)
    channels = Channel.query.all()
    return render_template("index.html", title='Home page', channels=channels, channel=channel, message_form=message_form)


@bp.route('/addChannel', methods=['GET', 'POST'])
@login_required
def add_channel():
    channel_form = CreateChannelForm()
    if channel_form.validate_on_submit():
        channel = Channel(name=channel_form.name.data,
                          purpose=channel_form.purpose.data, creator=current_user)
        db.session.add(channel)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template("channel.html", channel_form=channel_form, title="Add Channel")


@bp.route('/edit_channel/<channel_id>', methods=['Get', 'POST'])
@login_required
def edit_channel(channel_id):
    channel = Channel.query.get(int(channel_id))
    if channel is None:
        return render_template('errors/404.html'), 404

    old_ch_name = channel.name
    if current_user == channel.creator:
        edit_channel_form = CreateChannelForm(object=channel)
        if edit_channel_form.validate_on_submit():
            channel.name = edit_channel_form.name.data
            channel.purpose = edit_channel_form.purpose.data
            db.session.commit()
            print('channel has been edited')
            flash(f'channel with name {old_ch_name} has been edited to new name {channel.name} and purpose {channel.purpose}')
            return redirect(url_for('main.index_with_channel', channel_id = channel_id))
        edit_channel_form.name.data = channel.name
        edit_channel_form.purpose.data = channel.purpose
        return render_template("channel.html", channel_form=edit_channel_form, title=f"Edit Channel: {channel.name}", channel_id=channel_id)
        flash("you are not autherized to edit this channel")
    return redirect(url_for('main.index_with_channel', channel_id = channel_id))
    



@bp.route('/sendposts.json')
@login_required
def send_latest_posts():
    strtimestamp = request.args.get('timestamp')
    channel_id = request.args.get('channel_id')
    print("this is channel_id", channel_id)
    channel = Channel.query.get(channel_id)
    if channel:
        posts = channel.posts.filter(Post.timestamp > strtimestamp).all()
        if len(posts) > 0:
            list_of_parsed_posts = get_posts_parsed(posts)
            print(list_of_parsed_posts)
            post_response = {
                'is_available': True,
                'timestamp': datetime.utcnow(),
                'post_list': list_of_parsed_posts
            }
        else:
            post_response = {
                'is_available': False
            }
        json.dumps(post_response)
        return jsonify(post_response)


def get_posts_parsed(posts):
    list_of_parsed_posts = []
    post_dict = {}
    for post in posts:
        post_dict['username'] = post.author.username
        post_dict['img_url'] = post.author.avatar(70)
        post_dict['body'] = post.body
        print("post timestamp---->", post.timestamp)
        post_dict['timestamp'] = post.timestamp
        post_dict['utctimestr'] = str(post.timestamp)
        list_of_parsed_posts = list_of_parsed_posts + [post_dict]
        # list_of_parsed_posts['username'] = post.author.username
        # list_of_parsed_posts['img_url'] = post.author.avatar(70)
        # list_of_parsed_posts['body'] = post.body
        # list_of_parsed_posts['timestamp'] = post.timestamp
    return list_of_parsed_posts


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    posts, total = Post.search(g.search_form.q.data)
    return render_template('search.html', title='Search', posts=posts)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        print('now before request')
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/downloadallpost')
@login_required
def download():
    print('called')
    task = get_all_post.delay(current_user.id)
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}
    # return send_from_directory(directory = ".",filename = 'postsdata.json', as_attachment=True)


@bp.route('/status/<task_id>')
def taskstatus(task_id):
    task = get_all_post.AsyncResult(task_id)
    print(task.info)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']

    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@bp.route('/downloadpostsfile')
def sendallposts():
    return send_from_directory(directory=".", filename='postsdata.json', as_attachment=True)
