import re
import os
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, IntegerField, SelectField, RadioField, SubmitField, TextAreaField, FloatField
from wtforms.widgets import TextArea
from wtforms.validators import NumberRange, DataRequired, ValidationError

from db_parse import get_models

class TrainingsNewForm(FlaskForm):
    model_name = SelectField('Select Model: ')
    num_worker = IntegerField('Number of Worker: ')
    num_ps = IntegerField('Number of PS: ')
    num_epoch = IntegerField('Number of Epoch: ')
    train_option = RadioField('Train Option', choices = [('legacy', 'Continue from Existing Training'), ('new', 'Start a New Training')], default='new')
    train_label = SelectField('Training Label: ')
    mail_to = TextField('Send Mail: ')
    submit = SubmitField('Train')

class ModelsNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-z][a-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain lowercase letters numbers and dash')
        for model in get_models():
            if field.data == model[0]:
                raise  ValidationError('Model with name {} already exist'.format(field.data))

    model_name = TextField('Model Name: ', validators=[name_uniq_check])
    script =  TextField('Bash Script:', validators = [DataRequired()], widget=TextArea())
    image =  TextField('Container Image:', validators = [DataRequired()])
    desc = TextField('Description: ')
    submit = SubmitField('Save')

class ModelEditForm(FlaskForm):
    script =  TextAreaField('Bash Script:')
    desc = TextField('Description:')
    image =  TextField('Container Image:')
    submit = SubmitField('Update')

class ModelDeleteForm(FlaskForm):
    submit = SubmitField('Delete')

class EvalForm(FlaskForm):
    def dir_check(form, field):
        if field.data:
            if not os.path.isdir(field.data):
                raise ValidationError('Custom dir does not exist')

    log_dir = SelectField('Availabel Lables: ')
    custom_dir = TextField('Custom Dir: ', validators=[dir_check])
    submit = SubmitField('Load!')

class StopForm(FlaskForm):
    submit = SubmitField('Stop')

class ShowForm(FlaskForm):
    submit = SubmitField('show')

class KubecmdForm(FlaskForm):
    namespace = SelectField('namespace', choices = [('kube-system', 'kube-system'), ('default', 'default')])
    action = SelectField('action', choices = [('get', 'get'), ('describe', 'describe')])
    types = ['all', 'pods', 'nodes', 'svc', 'ds', 'ep', 'deploy', 'jobs', 'pv', 'pvc', 'events']
    target = SelectField('target', choices = [[type]*2 for type in types])
    submit = SubmitField('Execute')
