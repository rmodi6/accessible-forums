from flask import request
from flask_babel import _, lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Create a Post'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Type to search the forum'), validators=[DataRequired()])
    v = HiddenField(_l('version'), default="tree")
    n = HiddenField(_l('Number of search results'), default=10)

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
