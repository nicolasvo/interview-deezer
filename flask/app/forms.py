from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class ArtistForm(FlaskForm):
    artist = StringField('Artist')
    tag = StringField('Tag')
    date = StringField('Date')
    search = SubmitField('search artist')

class TagForm(FlaskForm):
    tag = StringField('Tag')
    search = SubmitField('search tag')

