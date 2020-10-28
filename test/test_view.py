import pytest
import bcrypt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
import json
import io

from app        import create_app
from sqlalchemy import create_engine, text
from unittest   import mock

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)

@pytest.fixture
@mock.patch('app.boto3')
def api(mock_boto3):
    mock_boto3.client.return_value = mock.Mock()
    
    app = create_app(config.test_config)
    app.config['TEST']  = True
    api                 = app.test_client()
    return api

def setup_function():
    hashed_password = bcrypt.hashpw('pw'.encode('utf-8'), bcrypt.gensalt())

    new_users   = [
        {
            'id'                : 1,
            'name'              : 'messi',
            'email'             : 'messi@',
            'profile'           : 'ten',
            'hashed_password'   : hashed_password
        },
        {
            'id'                : 2,
            'name'              : 'naldo',
            'email'             : 'naldo@',
            'profile'           : 'seven',
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
    database.execute(text("truncate tweets"))
    database.execute(text("truncate users_follow_list"))
    database.execute(text("set foreign_key_checks=1"))

def test_ping(api):
    resp    = api.get('/ping')
    assert b'pong' in resp.data

def test_login(api):
    resp    = api.post(
        '/login',
        data = json.dumps({
            'email'     : 'messi@',
            'password'  : 'pw'
        }),
        content_type    = 'application/json'
    )
    assert b"access_token" in resp.data

def test_unauthorized(api):
    resp = api.post(
        '/tweet',
        data            = json.dumps({'tweet' : 'gggg'}),
        content_type    = 'application/json'
    )
    assert resp.status_code == 401

    resp = api.post(
        '/follow',
        data            = json.dumps({'follow' : 2}),
        content_type    = 'application/json'
    )
    assert resp.status_code == 401
    
    resp = api.post(
        '/unfollow',
        data            = json.dumps({'unfollow' : 2}),
        content_type    = 'application/json'
    )
    assert resp.status_code == 401

def test_tweet(api):
    resp = api.post(
        '/login',
        data            = json.dumps({
            'email'     : 'messi@',
            'password'  : 'pw'
        }),
        content_type    = 'application/json'
   )
    resp_json       = json.loads(resp.data.decode('utf-8'))
    access_token    = resp.json['access_token']

    resp = api.post(
        '/tweet',
        data            = json.dumps({'tweet'   : 'hi naldo'}),
        content_type    = 'application/json',
        headers         = {'Authorization'  : access_token}
    )
    assert resp.status_code == 200

    resp = api.get('/timeline', headers = {'Authorization'  : access_token})
    timeline    = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert timeline == {
        'user_id'       : 1,
        'timeline'      : [
            {
                'user_id'   : 1,
                'tweet'     : 'hi naldo'
            }
        ]
    }

def test_follow(api):
    resp = api.post(
        '/login',
        data        = json.dumps({
            'email'     : 'messi@',
            'password'  : 'pw'
        }),
        content_type    = 'application/json'
    )
    resp_json       = json.loads(resp.data.decode('utf-8'))
    access_token    = resp_json['access_token']

    resp = api.get(
        '/timeline',
        headers = {'Authorization' : access_token}
    )
    timeline    = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == 200
    assert timeline == {
        'user_id'   : 1,
        'timeline'  : []
    }

    resp = api.post(
        '/follow',
        data        = json.dumps({
            'user_id'   : 1,
            'follow'    : 2
        }),
        content_type    = 'application/json',
        headers         = {'Authorization'  : access_token}
    )
    assert resp.status_code == 200

    resp = api.get(
        '/timeline',
        headers     = {'Authorization' : access_token}
    )
    timeline    = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert timeline     == {
        'user_id'   : 1,
        'timeline'  : [
            {
                'user_id'   : 2,
                'tweet'     : 'hi messi'
            }
        ]
    }


def test_unfollow(api):
    resp = api.post(
        '/login',
        data        = json.dumps({
            'email'     : 'messi@',
            'password'  : 'pw'
        }),
        content_type    = 'application/json'
    )
    resp_json       = json.loads(resp.data.decode('utf-8'))
    access_token    = resp_json['access_token']
    
    resp = api.post(
        '/follow',
        data    = json.dumps({
            'user_id'   : 1,
            'follow'    : 2
        }),
        content_type    = 'application/json',
        headers         = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    resp = api.get('timeline/1')
    timeline = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert timeline         == {
        'user_id'       : 1,
        'timeline'      : [
            {
                'user_id'       : 2,
                'tweet'         : 'hi messi'
            }
        ]
    }

    resp = api.post(
        '/unfollow',
        data        = json.dumps({
            'user_id'   : 1,
            'unfollow'  : 2
        }),
        content_type    = 'application/json',
        headers         = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    resp = api.get('/timeline/1')
    timeline    = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == 200
    assert timeline         == {
        'user_id'   : 1,
        'timeline'  : []
    }

def test_save_and_get_profile_picture(api):
    resp = api.post(
        '/login',
        data        = json.dumps({
            'email'     : 'messi@',
            'password'  : 'pw'
        }),
        content_type = 'application/json'
    )
    resp_json   = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.post(
        '/profile-picture',
        content_type    = 'multipart/form-data',
        headers         = {'Authorization' : access_token},
        data            = {'profile_pic' : (io.BytesIO(b'test image'), 'profile.png')}
    )

    assert resp.status_code == 200

    resp = api.get('/profile-picture/1')
    data = json.loads(resp.data.decode('utf-8'))

    assert data['img_url'] == f"{config.test_config['S3_BUCKET_URL']}profile.png"
