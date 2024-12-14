from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from app.database.models import User
from app.__init__ import db

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
        session['user_id'] = user.id
        return redirect(url_for('main.homepage'))
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    logout_user()
    return redirect(url_for('auth.login_post'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        group = request.form.get('group')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not group or not password:
            flash('All fields are required.', 'alert-danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'alert-danger')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            if user_exists.username == username:
                flash('Username already taken', 'alert-danger')
            elif user_exists.email == email:
                flash('Email already taken', 'alert-danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, group=group, password=generate_password_hash(password))

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'alert-success')
        return redirect(url_for('auth.login_post'))
    return render_template('register.html')