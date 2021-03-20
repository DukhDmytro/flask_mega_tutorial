"""
@app.route decorator creates an association between
the URL given as an argument and the function.
"""
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from guess_language import guess_language

from app import app, db

from app.models import User, Post
from .email import send_password_reset_email
from .fomrs import (
    LoginForm, RegistrationForm, EditProfileForm, EmptyForm,
    PostForm, ResetPasswordRequestForm, ResetPasswordForm
)
from .translate import translate


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == "UNKNOWN" or len(language) > 5:
            language = ''
        post = Post(
            body=form.post.data, author=current_user, language=language
        )
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))

    posts = current_user.followed_posts().paginate(
        page,
        app.config["POSTS_PER_PAGE"],
        False
    )
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None

    return render_template("index.html", posts=posts.items, form=form,
                           next_url=next_url, prev_url=prev_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid credentials"))
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", form=form, title=_("Sign In"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route("/user/<username>")
@login_required
def user_detail(username):
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'user_detail', username=user.username, page=posts.next_num
    ) if posts.has_next else None
    prev_url = url_for(
        'user_detail', username=user.username, page=posts.prev_num
    ) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, form=form,
                           next_url=next_url, prev_url=prev_url)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit() and request.method == "POST":
        current_user.about_me = form.about_me.data
        current_user.username = form.username.data
        db.session.commit()
        return redirect(url_for('user_detail', username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title=_("Edit profile"), form=form)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for("index"))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for("user_detail", username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for("user_detail", username=username))
    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', usernmae=username))
            return redirect(url_for("index"))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for("user_detail", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following', username=username))
        return redirect(url_for("user_detail", username=username))
    else:
        return redirect(url_for("index"))


@app.route("/explore")
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.timestamp.desc()
    ).paginate(page, app.config["POSTS_PER_PAGE"], False)
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title=_("All posts"), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))

    return render_template("reset_password_request.html", form=form, title=_('Password reset'))


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for("login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for("index"))

    return render_template('reset_password.html', form=form)


@app.route("/translate", methods=["POST"])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})