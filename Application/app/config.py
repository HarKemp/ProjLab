import os

class Config(object):
    ### App file upload settings
    # Holds all the temporary directories and files
    TEMP_FILE_DIRECTORY = 'temp'
    # Directories below are created under TEMP_FILE_DIRECTORY
    UPLOAD_FILE_DIRECTORY = 'uploads'
    REPORT_FILE_DIRECTORY = 'reports'
    # Max allowed file upload size in MiB (total size in one upload)
    MAX_UPLOAD_SIZE = 5
    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {'pdf'}

    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE * 1024 * 1024  # MiB

    ### Creates the directories for file storage in the TEMP_FILE_DIRECTORY
    BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), TEMP_FILE_DIRECTORY)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, UPLOAD_FILE_DIRECTORY)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    REPORT_FOLDER = os.path.join(BASE_DIR, REPORT_FILE_DIRECTORY)
    if not os.path.exists(REPORT_FOLDER):
        os.makedirs(REPORT_FOLDER)

# Development only (Sqlite config)
class DevConfig(Config):
    ### Database settings
    DB_INSTANCE_DIRECTORY = 'instance'
    DB_INSTANCE_NAME = 'test.db'
    SECRET_KEY = 'af28j093jf9wjfp9@J@*sajfaioj'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Creates directories that are necessary for sqlite db instance
    DATABASE_FOLDER = os.path.join(Config.BASE_DIR, DB_INSTANCE_DIRECTORY)
    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)

    DB_PATH = os.path.join(DATABASE_FOLDER, DB_INSTANCE_NAME)

    # Commented out to avoid WinError32 when running flask with the --debug flag
    #if os.path.exists(DB_PATH):
        #os.remove(DB_PATH)

    ### Defines path to sqlite database instance
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"