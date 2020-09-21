import jwt
import bcrypt
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import config

from model      import UserDao, TweetDao
from service    import UserService, TweetService
from sqlalchemy import create_engine, text
from unittest   import mock

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def user_service():
    mock_s3_client = mock.Mock()
    return UserService(UserDao(database), config.test_config, mock_s3_client)

@pytest.fixture
def tweet_service():
    return TweetService(TweetDao(database))

def setup_function():
    hashed_password = bcrypt.hashpw('pw'.encode('utf-8'), bcrypt.gensalt())

    new_users = [
        {
            'id'                : 1,
            'name'              : 'kim',
            'email'             : 'kim@',
            'profile'           : 'hahahahahaha',
            'hashed_password'   : hashed_password
        },
        {
            'id'                : 2,
            'name'              : 'lee',
            'email'             : 'lee@',
            'profile'           : 'kikikikikiki',
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
            'hi kim'
        )
    """))

def teardown_function():
    database.execute(text("set foreign_key_checks=0"))
    database.execute(text("truncate users"))
    database.execute(text("truncate tweets"))
    database.execute(text("truncate users_follow_list"))
    database.execute(text("set foreign_key_checks=1"))

def get_user(user_id):
    row = database.execute(text("""
        select 
            id,
            name,
            email,
            profile
        from users
        where id = :user_id
    """), {'user_id' : user_id}).fetchone()

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
        from users_follow_list
        where user_id = :user_id
    """), {
            'user_id'   : user_id
    }).fetchall()

    return [int(row['id']) for row in rows]
    
def test_create_new_user(user_service):
    new_user = {
        'name'              : 'park',
        'email'             : 'park@',
        'profile'           : 'huhuhuhuhu',
        'password'          : 'pw'
    }
    new_user_id = user_service.create_new_user(new_user)
    created_user = get_user(new_user_id)

    assert created_user == {
        'id'                : new_user_id,
        'name'              : 'park',
        'email'             : 'park@',
        'profile'           : 'huhuhuhuhu'
    }

def test_login(user_service):
    assert user_service.login({
        'email'     : 'kim@',
        'password'  : 'pw'
    })
    
    assert user_service.login({
        'email'     : 'kim@',
        'password'  : 'fake'
    })
    
def test_generate_access_token(user_service):
    token = user_service.generate_access_token(1)
    payload = jwt.decode(token, config.JWT_SECRET_KEY, 'HS256')

    assert payload['user_id'] == 1

def test_follow(user_service):
    user_service.follow(1,2)
    follow_list = get_follow_list(1)

    assert follow_list == [2]

def test_unfollow(user_service):
    user_service.follow(1,2)
    user_service.unfollow(1,2)
    follow_list = get_follow_list(1)

    assert follow_list == []

def test_tweet(tweet_service):
    tweet_service.tweet(1, 'hi lee')
    timeline = tweet_service.timeline(1)
    
    assert timeline == [{
        'user_id'   : 1,
        'tweet'     : 'hi lee'
    }]

def test_timeline(tweet_service, user_service):
    tweet_service.tweet(1, 'hi lee')
    tweet_service.tweet(2, 'bye kim')
    user_service.follow(1,2)
    timeline    = tweet_service.timeline(1)

    assert timeline == [
        {
            'user_id'   : 2,
            'tweet'     : 'hi kim'
        },
        {
            'user_id'   : 1,
            'tweet'     : 'hi lee'
        },
        {
            'user_id'   : 2,
            'tweet'     : 'bye kim'
        }
    ]

def test_save_and_get_profile_picture(user_service):
    user_id = 1
    user_profile_picture = user_service.get_profile_picture(user_id)
    assert user_profile_picture is None

    test_pic = mock.Mock()
    filename = 'test.png'
    user_service.save_profile_picture(test_pic, filename, user_id)

    actual_profile_picture = user_service.get_profile_picture(user_id)
    assert actual_profile_picture == 'http://s3.ap-northeast-2.amazonaws.com/test/test.png'
