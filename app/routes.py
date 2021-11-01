from flask import render_template

from app import app


@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    context = {
        'user': {'username': 'Dima'},
        'title': 'Home',
        'posts': posts,
    }

    return render_template('index.html', **context)
