from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    power = IntegerField('Alaraja ohjaukselle (W) (200-3000)',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    start = IntegerField('Aloitusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    stop = IntegerField('Lopetusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Update')

class UpdateRaneForm(FlaskForm):
    power = IntegerField('Alaraja Rele 1 (670W)',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    power1 = IntegerField('Alaraja Rele2 (1500W) ',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    power2 = IntegerField('Alaraja Rele1+Rele2 (2170W)',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    power3 = IntegerField('Alaraja Rele3 (3000W)',validators=[DataRequired(), NumberRange(min=200, max=3000, message="Out of range")])
    start = IntegerField('Aloitusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    stop = IntegerField('Lopetusaika (1-23)',validators=[DataRequired(), NumberRange(min=1, max=23, message="Out of range")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Update')
