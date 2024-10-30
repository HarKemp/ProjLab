from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    ### Set up database
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        from app.prodConfig import ProdConfig
        app.config.from_object(ProdConfig)
    else:
        from app.config import DevConfig
        app.config.from_object(DevConfig)

    ### Connect to database 
    db.init_app(app)

    ### Create Test User On SQLite Database
    from app.db.models import User
    if env == 'development':
        # Create SQLite database tables
        with app.app_context():
            db.create_all()

            # Test user credentials
            test_username = "test"
            test_password = "cilveks"

            # Check if the test user already exists and if not, create him
            if not User.query.filter_by(username=test_username).first():
                from werkzeug.security import generate_password_hash

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
    from .ocr import ocr as ocr_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(ocr_blueprint)

    return app

