from app import app, db
from app.forms import LoginForm
from app.models import DbUser, FeedUser, UserList#UserFollows
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from atproto import IdResolver, Client
import sqlalchemy as sa
import os
from dotenv import load_dotenv

load_dotenv()

idr = IdResolver()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = db.session.scalar(sa.select(FeedUser).where(FeedUser.id == current_user.feeduser_id))

    user_handle = idr.did.resolve(user.did)

    bsky_client = Client("https://bsky.social")
    bsky_client.login(os.environ.get('HANDLE'), os.environ.get('PASSWORD'))

    more_follows = True
    cursor = ''

    handles = []

    while more_follows:
        res = bsky_client.get_follows(actor=user.did, cursor=cursor, limit=100)

        if res['follows']:
            handles += [f.handle for f in res['follows']]

        if res['cursor']:
            cursor = res['cursor']
        else:
            more_follows = False

    subscribed_to = db.session.scalars(sa.select(UserList).where(UserList.feeduser_id==current_user.feeduser_id)).all()


    #subscribed_to_handles = []
    #for elem in subscribed_to:
    #    handle = idr.did.resolve(elem.subscribes_to_did).also_known_as[0]
    #    subscribed_to_handles.append(handle)

    return render_template("index.html", follows=handles, user_handle=user_handle, subscribed_to=subscribed_to)

@app.route('/add', methods=['POST']) 
def add():
    add_user_handle = request.form['add_user_handle']
    add_user_did = idr.handle.resolve(add_user_handle)

    if add_user_did is None:
        flash(f'Bluesky user {add_user_handle} does not exist')
        return redirect(url_for('index')) 

    userlist_entry = UserList(feeduser_id=current_user.feeduser_id, subscribes_to_did=add_user_did)
    db.session.add(userlist_entry) 
    db.session.commit() 
  
    return redirect(url_for('index'))

@app.route("/delete/<int:ul_id>")
def delete(ul_id):
    #todo = Todo.query.filter_by(id=todo_id).first()
    #db.session.delete(todo)
    remove_user = db.session.scalar(sa.select(UserList).where(UserList.id == ul_id))
    db.session.delete(remove_user)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_did = idr.handle.resolve(form.username.data)
        print(user_did)

        if user_did:
            #user = db.session.scalar(sa.select(DbUser).where(DbUser.user_handle == form.username.data))
            user = db.session.scalar(sa.select(DbUser).join(FeedUser, DbUser.feeduser_id == FeedUser.id).where(FeedUser.did == user_did))
        else:
            user = None

        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))