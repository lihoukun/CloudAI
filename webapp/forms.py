import re
import os
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, ValidationError

from database import TemplateModel, TrainingModel


class TrainingsNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-z][a-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain lowercase letters numbers and dash')
        for t in TrainingModel.query.all():
            if field.data == t.name:
                raise  ValidationError('Training with label {} already exist'.format(field.data))

    train_name = StringField('Training Label: ', validators=[name_uniq_check])
    template_name = SelectField('Select Template: ')
    num_gpu = IntegerField('Number of Worker: ')
    num_cpu = IntegerField('Number of PS: ')
    num_epoch = IntegerField('Number of Epoch: ')
    mail_to = StringField('Send Mail: ')
    submit = SubmitField('Train')


class TrainingResumeForm(FlaskForm):
    num_worker = IntegerField('Number of Worker: ')
    num_ps = IntegerField('Number of PS: ')
    num_epoch = IntegerField('Number of Epoch: ')
    mail_to = StringField('Send Mail: ')
    submit = SubmitField('Train')


class TemplatesNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-z][a-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain lowercase letters numbers and dash')
        for t in TemplateModel.query.all():
            if field.data == t.name:
                raise  ValidationError('Template with name {} already exist'.format(field.data))

    name = StringField('Template Name: ', validators=[name_uniq_check])
    script = StringField('Bash Script:', validators = [DataRequired()], widget=TextArea())
    image = StringField('Container Image:', validators = [DataRequired()])
    log_dir = StringField('Tensorboard Load Dir for TF')
    mnt_option = SelectField('Select Mnt Option:', choices=[('HOSTPATH', 'HOSTPATH')], default='HOSTPATH')
    desc = StringField('Description: ')
    submit = SubmitField('Save')


class TemplatesEditForm(FlaskForm):
    script = StringField('Bash Script:', validators = [DataRequired()], widget=TextArea())
    image = StringField('Container Image:', validators = [DataRequired()])
    log_dir = StringField('Tensorboard Load Dir for TF')
    mnt_option = SelectField('Select Mnt Option:', choices=[('HOSTPATH', 'HOSTPATH')], default='HOSTPATH')
    desc = StringField('Description: ')
    submit = SubmitField('Save')


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


class EvalForm(FlaskForm):
    def dir_check(form, field):
        if field.data:
            if not os.path.isdir(field.data):
                raise ValidationError('Custom dir does not exist')

    log_dir = SelectField('Availabel Lables: ')
    custom_dir = StringField('Custom Dir: ', validators=[dir_check])
    submit = SubmitField('Load!')


class StopForm(FlaskForm):
    submit = SubmitField('Stop')


class ShowForm(FlaskForm):
    submit = SubmitField('Show')


class KubecmdForm(FlaskForm):
    namespace = SelectField('namespace', choices = [('kube-system', 'kube-system'), ('default', 'default')])
    action = SelectField('action', choices = [('get', 'get'), ('describe', 'describe')])
    types = ['all', 'pods', 'nodes', 'svc', 'ds', 'ep', 'deploy', 'jobs', 'pv', 'pvc', 'events']
    target = SelectField('target', choices = [[type]*2 for type in types])
    submit = SubmitField('Execute')
