from flask import render_template, flash, redirect, url_for

from app import app
from .froms import LoginForm


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login for user {form.username.data}. Remember: {form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)
