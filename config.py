db = {
    'user'          : 'root',
    'password'      : 'mksql123',
    'host'          : 'python-backend-test.cs3ybsej01vv.ap-northeast-2.rds.amazonaws.com',
    'port'          : 3306,
    'database'      : 'miniter'
}

DB_URL      = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

JWT_SECRET_KEY = 'KEY'

test_db ={
    'user'      : 'root',
    'password'  : 'mksql123',
    'host'      : 'localhost',
    'port'      : 3306,
    'database'  : 'miniter'
}

test_config = {
    'DB_URL' : f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8",
    'JWT_SECRET_KEY' : 'KEY',
    'S3_BUCKET'       : 'test',
    'S3_ACCESS_KEY'   : 'test_access_key',
    'S3_SECRET_KEY'   : 'test_secret_key',
    'S3_BUCKET_URL'   : f"http://s3.ap-northeast-2.amazonaws.com/test/"   
}

UPLOAD_DIRECTORY = './profile_pictures'

S3_BUCKET       = 'ooknimms3'
S3_ACCESS_KEY   = 'AKIAY2ZCBHBXWHRZ3JSL'
S3_SECRET_KEY   = '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'
S3_BUCKET_URL   = f"http://{S3_BUCKET}.s3.ap-northeast-2.amazonaws.com/"
