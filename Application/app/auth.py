from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from app.db.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        # Get user input from login.html
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if user is in database
        user = User.query.filter_by(username=username).first()
        # Check hashed password against password stored in database
        if not user or not check_password_hash(user.password, password):
            flash('Incorrect username or password')
            # Reload page if incorrect credentials
            return redirect(url_for('auth.login_post'))
        # If credentials correct - log in user and redirect to home page
        login_user(user)
        return redirect(url_for('main.homepage'))
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_post'))
