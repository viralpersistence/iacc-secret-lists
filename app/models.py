from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin

class FeedUser(db.Model):
    __tablename__ = 'feeduser'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    did: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, unique=True)
    replies_off: so.Mapped[bool] = so.mapped_column(sa.Boolean)


class DbUser(UserMixin, db.Model):
    __tablename__ = 'dbuser'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    password: so.Mapped[str] = so.mapped_column(sa.String(20), index=True)

    def __repr__(self):
        return '<User {}>'.format(self.user_handle)

'''
class UserFollows(db.Model):
    __tablename__ = 'userfollows'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    follows_did: so.Mapped[str] = so.mapped_column(sa.String(255))
    uri: so.Mapped[str] = so.mapped_column(sa.String(255))
'''

class UserList(db.Model):
    __tablename__ = 'userlist'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    feeduser_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    subscribes_to_did: so.Mapped[str] = so.mapped_column(sa.String(255))


@login.user_loader
def load_user(id):
    return db.session.get(DbUser, int(id))