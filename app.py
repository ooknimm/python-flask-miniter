from sqlalchemy         import create_engine
from flask              import Flask
from model              import UserDao, TweetDao
from service            import UserService, TweetService
from view               import create_endpoints
import boto3
import config

class Services:
    pass


def create_app(test_config=None):
    
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)

    user_dao    = UserDao(database)
    tweet_dao   = TweetDao(database)

    s3_client = boto3.client(
        's3',
        aws_access_key_id       = app.config['S3_ACCESS_KEY'],
        aws_secret_access_key   = app.config['S3_SECRET_KEY']
    )
    services        = Services
    services.user_service    = UserService(user_dao, app.config, s3_client)
    services.tweet_service   = TweetService(tweet_dao)

    create_endpoints(app, services)

    return app
