from app import app, db
from app.forms import LoginForm
from app.models import DbUser, FeedUser, UserList, UserFollows
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from atproto import IdResolver, Client
from app.helpers import load_user_follows
import sqlalchemy as sa
import os
import requests
from dotenv import load_dotenv

load_dotenv()

idr = IdResolver()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = db.session.scalar(sa.select(FeedUser).where(FeedUser.id == current_user.feeduser_id))
    user_handle = idr.did.resolve(user.did).get_handle()

    ufs = db.session.scalars(sa.select(UserFollows).where(UserFollows.feeduser_id == current_user.feeduser_id)).all()
    handles = [uf.follows_handle for uf in ufs]

    subscribed_to = db.session.scalars(sa.select(UserList).where(UserList.feeduser_id==current_user.feeduser_id).order_by(UserList.subscribes_to_disp_name)).all()

    return render_template("index.html", follows=handles, user_handle=user_handle, subscribed_to=subscribed_to)

@app.route('/add', methods=['POST'])
def add():
    add_user_handle = request.form['add_user_handle']
    add_user_did = idr.handle.resolve(add_user_handle)
    #add_user_disp_name = 

    if add_user_did is None:
        flash(f'Bluesky user {add_user_handle} does not exist')
        return redirect(url_for('index')) 

    actor = requests.get(
        "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile",
        params={
            "actor": add_user_did,
        }
    ).json()

    add_user_disp_name = actor['displayName']

    if 'displayName' not in actor:
        flash(f'Bluesky user {add_user_handle} does not exist')
        return redirect(url_for('index')) 
    else:
        add_user_disp_name = actor['displayName']

    

    userlist_entry = UserList(feeduser_id=current_user.feeduser_id, subscribes_to_did=add_user_did, subscribes_to_handle=add_user_handle, subscribes_to_disp_name=add_user_disp_name)
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
        user_password = form.password.data
        print(user_did)

        if user_did:
            user = db.session.scalar(sa.select(DbUser).join(FeedUser, DbUser.feeduser_id == FeedUser.id).where(sa.and_(FeedUser.did == user_did, DbUser.password == user_password)))
        else:
            user = None

        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        load_user_follows(user)
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