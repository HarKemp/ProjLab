from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():

    testing = True

    app = Flask(__name__)

    ### Set up database
    if not testing:
        # PRODUCTION: MySQL Database
        username = "develop"
        password = "cilveksviens$3"
        hostname = "localhost" ## "labdarbs.westeurope.cloudapp.azure.com"
        dbname = "appusers"
        dbpath = f'mysql+pymysql://{username}:{password}@{hostname}/{dbname}'
    else:
        # TESTING: SQLite Database
        dbpath = 'sqlite:///test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    ### Connect to database 
    app.config['SECRET_KEY'] = 'af28j093jf9wjfp9@J@*sajfaioj'
    app.config['SQLALCHEMY_DATABASE_URI'] = dbpath
    db.init_app(app)

    ### Create Test User On SQLite Database
    from app.db.models import User
    if testing:
        # Create SQLite database tables
        with app.app_context():
            db.create_all()

            # Create a test user
            from werkzeug.security import generate_password_hash
            test_username = "students"
            test_password = "cilveks"
            new_user = User(username=test_username, password=generate_password_hash(test_password))
            
            # Add test user to database
            db.session.add(new_user)
            db.session.commit()


    ### User login management 
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_post'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    ### Route Blueprints
    # blueprint for auth
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for main
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

