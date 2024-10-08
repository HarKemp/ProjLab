class Config(object):
    SECRET_KEY = 'af28j093jf9wjfp9@J@*sajfaioj' # pagaidām šo nevajag
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ConfigDevelop(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ConfigProd(Config):
    username = 'develop'
    password = 'cilveksviens$3'
    hostname = 'localhost'
    dbname = 'appusers'

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{hostname}/{dbname}'