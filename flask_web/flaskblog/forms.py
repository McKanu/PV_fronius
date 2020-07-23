from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    power = IntegerField('Alaraja ohjaukselle (W)',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    start = IntegerField('Aloitusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    stop = IntegerField('Lopetusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Update')

class UpdateRaneForm(FlaskForm):
    power = IntegerField('Alaraja Rele1',validators=[DataRequired(), NumberRange(min=200, max=700, message="Out of range")])
    power1 = IntegerField('Alaraja Rele2',validators=[DataRequired(), NumberRange(min=700, max=1400, message="Out of range")])
    power2 = IntegerField('Alaraja Rele1+Rele2',validators=[DataRequired(), NumberRange(min=1400, max=2000, message="Out of range")])
    power3 = IntegerField('Alaraja Rele2+Rele3',validators=[DataRequired(), NumberRange(min=2000, max=4000, message="Out of range")])
    start = IntegerField('Aloitusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    stop = IntegerField('Lopetusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Update')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

