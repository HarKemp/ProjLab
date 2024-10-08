import os

class Config(object):
    SECRET_KEY = 'af28j093jf9wjfp9@J@*sajfaioj'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Creates the instance db file in Application/instance directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_DIR = os.path.join(BASE_DIR, 'instance')
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATABASE_DIR, 'test.db')}"