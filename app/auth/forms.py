from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=(DataRequired(), ))
    password = PasswordField(_l("Password"), validators=(DataRequired(), ))
    remember_me = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Sign in"))


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=(DataRequired(), ))
    email = StringField(_l("Email"), validators=(DataRequired(), Email()))
    password = PasswordField(_l("Password"), validators=(DataRequired(), ))
    password2 = PasswordField(
        _l("Repeat password"), validators=(DataRequired(), EqualTo('password'))
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(_l("Please use a different username"))

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError(_l("Please user a different email"))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=(Email(), DataRequired()))
    submit = SubmitField(_l('Submit'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=(DataRequired(),))
    password2 = PasswordField(
        _l("Repeat password"), validators=(DataRequired(), EqualTo('password'))
    )
    submit = SubmitField(_l("Register"))
