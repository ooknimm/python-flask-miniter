db = {
    'user'          : 'root',
    'password'      : 'mksqlpw123',
    'host'          : 'python-backend-test.cs3ybsej01vv.ap-northeast-2.rds.amazonaws.com',
    'port'          : 3306,
    'database'      : 'miniter'
}

DB_URL      = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

JWT_SECRET_KEY = 'KEY'

test_db ={
    'user'      : 'root',
    'password'  : '1q2w',
    'host'      : 'localhost',
    'port'      : 3306,
    'database'  : 'minitor'
}

test_config = {
    'DB_URL' : f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8",
    'JWT_SECRET_KEY' : 'KEY'
}
