from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class UploadForm(FlaskForm):
    file = FileField('EVTX File', validators=[DataRequired()])
    submit = SubmitField('Upload and Parse')

class SearchForm(FlaskForm):
    event_id = StringField('Event ID')
    provider = StringField('Provider')
    level = SelectField('Level', choices=[('', 'All'), ('Information', 'Information'), 
                                          ('Warning', 'Warning'), ('Error', 'Error'), 
                                          ('Critical', 'Critical')])
    keyword = StringField('Keyword Search')
    submit = SubmitField('Search')
