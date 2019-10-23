from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileRequired
from models import User


class AddEpisodeForm(FlaskForm):

    # Basic Fields
    epname = StringField('Name', validators=[DataRequired()])
    epnum = StringField('Number', validators=[DataRequired()])
    eplink = StringField('Link', validators=[DataRequired()])
    epdesc = TextAreaField('Description', validators=[Length(min=0, max=140)])
    epaudio = FileField('Audio',validators=[FileRequired()])

    # Itunes Fields
    it_sum = TextAreaField('Itunes Summary', validators=[Length(min=0, max=140)])
    it_subtitle = StringField('Itunes Subtitle', validators=[DataRequired(), Length(min=0, max=255)])

    submit = SubmitField('Add_Episode')


class AddPodcastForm(FlaskForm):

    # Basic Fields
    author = StringField('Author', validators=[DataRequired()])
    podname = StringField('Title', validators=[DataRequired()])
    #podlink = StringField('Podcast Link', validators=[DataRequired()])
    podicon = FileField('Icon',validators=[FileRequired()])
    poddesc = TextAreaField('Description', validators=[Length(min=0, max=140)])

    # Itunes Fields
    it_own_name = StringField('Itunes Owners Name', validators=[DataRequired()])
    it_own_email = StringField('Itunes Owners Email', validators=[DataRequired()])
    it_cat = StringField('Itunes Category', validators=[DataRequired()])
    it_subcat = StringField('Itunes Subcategory', validators=[DataRequired()])
    it_sum = TextAreaField('Itunes Summary', validators=[Length(min=0, max=140)])
    it_subtitle = StringField('Itunes Subtitle', validators=[DataRequired()])
    it_keys = StringField('Itunes Keys', validators=[DataRequired()])
    it_explicit = StringField('Itunes Explicit (yes/no)', validators=[DataRequired()])

    # Other Fields
    submit = SubmitField('Add_Podcast')


class EditEpisodeForm(FlaskForm):

    # Basic Fields
    epname = StringField('Name', validators=[DataRequired()])
    epnum = StringField('Number', validators=[DataRequired()])
    eplink = StringField('Link', validators=[DataRequired()])
    epdesc = TextAreaField('Description', validators=[Length(min=0, max=140)])
    epaudio = FileField('Audio',validators=[FileRequired()])

    # Itunes Fields
    it_sum = TextAreaField('Itunes Summary', validators=[Length(min=0, max=140)])
    it_subtitle = StringField('Itunes Subtitle', validators=[DataRequired(), Length(min=0, max=255)])

    submit = SubmitField('Edit_Episode')


class EditPodcastForm(FlaskForm):

    # Basic Fields
    author = StringField('Author', validators=[DataRequired()])
    podname = StringField('Title', validators=[DataRequired()])
    #podlink = StringField('Podcast Link', validators=[DataRequired()])
    podicon = FileField('Icon',validators=[FileRequired()])
    poddesc = TextAreaField('Description', validators=[Length(min=0, max=140)])

    # Itunes Fields
    it_own_name = StringField('Itunes Owners Name', validators=[DataRequired()])
    it_own_email = StringField('Itunes Owners Email', validators=[DataRequired()])
    it_cat = StringField('Itunes Category', validators=[DataRequired()])
    it_subcat = StringField('Itunes Subcategory', validators=[DataRequired()])
    it_sum = TextAreaField('Itunes Summary', validators=[Length(min=0, max=140)])
    it_subtitle = StringField('Itunes Subtitle', validators=[DataRequired()])
    it_keys = StringField('Itunes Keys', validators=[DataRequired()])
    it_explicit = StringField('Itunes Explicit (yes/no)', validators=[DataRequired()])

    # Other Fields
    submit = SubmitField('Edit_Podcast')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

