"""
@app.route decorator creates an association between
the URL given as an argument and the function.
"""
from flask import render_template, flash, redirect, url_for
from app import app

from .fomrs import LoginForm


@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'Dmytro'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Kropyvnytskyi!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so bad!'
        }
    ]
    return render_template("index.html", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('logined')
        return redirect(url_for("index"))
    return render_template("login.html", form=form, title="Sign In")
