from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=1, max=64)], render_kw={'class': 'form-control'})
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=1, max=128)], render_kw={'class': 'form-control'})
    remember_me = BooleanField(label='Remember Me', render_kw={'class': 'form-check-label'})
    submit = SubmitField(label='Sign In', render_kw={'class': 'btn btn-primary', 'type': 'submit'})


class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=1, max=64)], render_kw={'class': 'form-control', 'id': 'username-field'})
    email = StringField(label='Email', validators=[DataRequired(), Length(min=1, max=120), Email()], render_kw={'class': 'form-control'})
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=1, max=128)], render_kw={'class': 'form-control'})
    password2 = PasswordField(label='Repeat Password', validators=[DataRequired(), Length(min=1, max=128), EqualTo('password')], render_kw={'class': 'form-control'})
    submit = SubmitField(label='Register', render_kw={'class': 'btn btn-primary', 'type': 'submit'})

    # check for duplicate username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(message='Please user a different username.')

    # check for duplicate email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(message='Please user a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=1, max=64)], render_kw={'class': 'form-control'})
    about_me = TextAreaField(label='About Me', validators=[Length(min=0, max=140)], render_kw={'class': 'form-control'})
    submit = SubmitField(label='Submit', render_kw={'class': 'btn btn-primary', 'type': 'submit'})

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError(message='Please user a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(label='What you have in mind?', validators=[DataRequired(), Length(min=1, max=140)], render_kw={'class': 'form-control'})
    submit = SubmitField(label='Submit', render_kw={'class': 'btn btn-primary', 'type': 'submit'})
