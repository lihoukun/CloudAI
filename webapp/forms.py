import re
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, IntegerField, SelectField, RadioField, SubmitField, TextAreaField, FloatField
from wtforms.widgets import TextArea
from wtforms.validators import NumberRange, DataRequired, ValidationError

from db_parse import get_models

class TrainingsNewForm(FlaskForm):
    model_name = SelectField('Select Model: ')
    num_gpu = IntegerField('Number of GPU: ')
    num_cpu = IntegerField('Number of CPU: ')
    num_epoch = FloatField('Number of Epoch: ')
    train_option = RadioField('Train Option', choices = [('legacy', 'Continue from Existing Training'), ('new', 'Start a New Training')], default='new')
    train_label = SelectField('Training Label: ')
    submit = SubmitField('Train')

class ModelsNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-zA-Z][A-Za-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain letters numbers and dash')
        for model in get_models():
            if field.data == model[0]:
                raise  ValidationError('Model with name {} already exist'.format(field.data))

    model_name = TextField('Model Name: ', validators=[name_uniq_check])
    script =  TextField('Bash Script:', validators = [DataRequired()], widget=TextArea())
    desc = TextField('Description: ')
    submit = SubmitField('Save')

class ModelEditForm(FlaskForm):
    script =  TextAreaField('Bash Script:')
    desc = TextField('Description: ')
    submit = SubmitField('Save')

class EvalForm(FlaskForm):
    log_dir = SelectField('LOG Directory: ')
    submit = SubmitField('Start TensorBoard')

class StopForm(FlaskForm):
    submit = SubmitField('Stop')

class ShowForm(FlaskForm):
    submit = SubmitField('show')

class KubecmdForm(FlaskForm):
    def label_format_check(form , field):
        if ' ' in field.data:
            raise ValidationError('Label cannot contain space')
        for pair in field.data.split(','):
            tmp = pair.split('=')
            if len(tmp) != 2:
                raise ValidationError("Each Label pair needs like key=value")
            if not tmp[0]:
                raise ValidationError("Key cannot be empty")
            if not tmp[1]:
                raise ValidationError("Value cannot be empty")
    action = SelectField('action', choices = [('get all', 'get all'), ('describe all', 'describe all'), ('logs', 'logs')])
    label_str = TextField('label', validators=[label_format_check])
    submit = SubmitField('Execute')
