from flask import Blueprint
from flask import render_template
from flask_login import login_required

main = Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template("login.html")

@main.route("/homepage", methods=['GET', 'POST'])
@login_required
def homepage():
    return render_template("homepage.html")
