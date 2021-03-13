"""
@app.route decorator creates an association between
the URL given as an argument and the function.
"""
from flask import render_template
from app import app


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
