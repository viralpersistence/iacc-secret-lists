from atproto import IdResolver, Client
from dotenv import load_dotenv
from app.models import db, FeedUser, UserList
import os
import sqlalchemy as sa

load_dotenv()
idr = IdResolver()

def load_user_follows(current_user):
    user = db.session.scalar(sa.select(FeedUser).where(FeedUser.id == current_user.feeduser_id))

    bsky_client = Client("https://bsky.social")
    bsky_client.login(os.environ.get('HANDLE'), os.environ.get('PASSWORD'))

    more_follows = True
    cursor = ''

    #follows = []

    while more_follows:
        res = bsky_client.get_follows(actor=user.did, cursor=cursor, limit=100)

        if res['follows']:
            print(res['follows'][0])
            #f += [f.handle for f in res['follows']]

            follows = [{'temp_did': f.did, 'temp_handle': f.handle, 'temp_disp_name': f.display_name} for f in res['follows']]
            print(follows)

        if res['cursor']:
            cursor = res['cursor']
        else:
            more_follows = False

    subscribed_to = db.session.scalars(sa.select(UserList).where(UserList.feeduser_id==current_user.feeduser_id)).all()