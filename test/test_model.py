import bcrypt
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import config

from model      import UserDao, TweetDao
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)

@pytest.fixture
def user_dao():
    return UserDao(database)

@pytest.fixture
def tweet_dao():
    return TweetDao(database)

def setup_function():
    hashed_password = bcrypt.hashpw(b'pw', bcrypt.gensalt())
    new_users = [
        {
            'id'                : 1,
            'name'              : 'messi',
            'email'             : 'messi@',
            'profile'           : 'yeah',
            'hashed_password'   : hashed_password
        },
        {
            'id'                : 2,
            'name'              : 'naldo',
            'email'             : 'naldo@',
            'profile'           : 'hou',
            'hashed_password'   : hashed_password
        }
    ]
    database.execute(text("""
        insert into users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) values (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_users)

    database.execute(text("""
        insert into tweets (
            user_id,
            tweet
        ) values (
             2,
            'hi messi'
        )
    """))

def teardown_function():
    database.execute(text("set foreign_key_checks=0"))
    database.execute(text("truncate users"))
    database.execute(text("truncate users_follow_list"))
    database.execute(text("truncate tweets"))
    database.execute(text('set foreign_key_checks=1'))

def get_user(user_id):
    row = database.execute(text("""
        select
            id,
            name,
            email,
            profile
        from users
        where id = :user_id
    """),{'user_id' : user_id}).fetchone()

    return {
        'id'        : row['id'],
        'name'      : row['name'],
        'email'     : row['email'],
        'profile'   : row['profile']
    } if row else None

def get_follow_list(user_id):
    rows = database.execute(text("""
        select 
            follow_user_id as id
        from 
            users_follow_list
        where
            user_id = :user_id
    """), {'user_id' : user_id}).fetchall()

    return [int(row['id'])for row in rows]

def test_insert_user(user_dao):
    new_user = {
        'name'      : 'kaka',
        'email'     : 'kaka@',
        'profile'   : 'haha',
        'password'  : 'pw'
    }
    new_user_id = user_dao.insert_user(new_user)
    user        = get_user(new_user_id)

    assert user == {
        'id'        : new_user_id,
        'name'      : new_user['name'],
        'email'     : new_user['email'],
        'profile'   : new_user['profile']
    }

def test_get_id_and_password(user_dao):
    
    user_credential = user_dao.get_user_id_and_password(email='messi@')
    
    assert user_credential['id'] == 1
    assert bcrypt.checkpw('pw'.encode('utf-8'), user_credential['hashed_password'].encode('utf-8'))

def test_insert_follow(user_dao):
    
    user_dao.insert_follow(user_id=1, follow_id=2)

    follow_list = get_follow_list(1)

    assert follow_list == [2]

def test_insert_unfollow(user_dao):

    user_dao.insert_follow(user_id=1,follow_id=2)
    user_dao.insert_unfollow(user_id=1, unfollow_id=2)

    follow_list = get_follow_list(1)
    assert follow_list == []

def test_insert_tweet(tweet_dao):

    tweet_dao.insert_tweet(1,'hi naldo')
    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id'   : 1,
            'tweet'     : 'hi naldo'
        }
    ]

def test_timeline(user_dao, tweet_dao):
    tweet_dao.insert_tweet(1, 'hi naldo')
    tweet_dao.insert_tweet(2, 'bye messi')
    user_dao.insert_follow(1,2)
    
    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id'   : 2,
            'tweet'     : 'hi messi'
        },
        {
            'user_id'   : 1,
            'tweet'     : 'hi naldo'
        },
        {
            'user_id'   : 2,
            'tweet'     : 'bye messi'
        }
    ]
