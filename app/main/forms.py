from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import DataRequired, ValidationError, Length
from flask import request


class PostForm(FlaskForm):
    post = TextField('Post a message on channel', validators=[DataRequired(), Length(min=1,max=140)])
    submit = SubmitField('submit')
 
class CreateChannelForm(FlaskForm):
    name = TextField('name', validators=[DataRequired(), Length(min=1,max=140)])
    purpose = TextField('purpose', validators=[DataRequired(), Length(min=1,max=140)])
    submit = SubmitField('submit')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
