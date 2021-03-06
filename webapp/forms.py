import re
import os
import json
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from wtforms.widgets import TextArea
from database import TemplateModel, TrainingModel


class TrainingsNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-z][a-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain lowercase letters numbers and dash')
        for t in TrainingModel.query.all():
            if field.data == t.name:
                raise ValidationError('Training with label {} already exist'.format(field.data))

    def params_format_check(form, field):
        if field.data:
            if re.search("'", field.data):
                raise ValidationError('params cannot contain single quote')
            try:
                json.loads(field.data)
            except:
                raise ValidationError('Not valid json format')

    train_name = StringField('Training Label: ', validators=[name_uniq_check])
    template_name = SelectField('Select Template: ')
    num_gpu = IntegerField('Number of Worker: ')
    num_cpu = IntegerField('Number of PS: ')
    params = StringField('Hyper Params in json: ', validators=[params_format_check])
    mail_to = StringField('Send Mail: ')
    submit = SubmitField('Train')


class TrainingResumeForm(FlaskForm):
    def params_format_check(form, field):
        if field.data:
            if re.search("'", field.data):
                raise ValidationError('params cannot contain single quote')
            try:
                json.loads(field.data)
            except:
                raise ValidationError('Not valid json format')

    num_gpu = IntegerField('Number of Worker: ')
    num_cpu = IntegerField('Number of PS: ')
    params = StringField('Hyper Params in json: ', validators=[params_format_check])
    mail_to = StringField('Send Mail: ')
    submit = SubmitField('Resume Training')


class TemplatesNewForm(FlaskForm):
    def name_uniq_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if not re.match(r'^[a-z][a-z0-9-]*$', field.data):
            raise ValidationError('Name must start with letter, and can only contain lowercase letters numbers and dash')
        for t in TemplateModel.query.all():
            if field.data == t.name:
                raise ValidationError('Template with name {} already exist'.format(field.data))

    def cmd_format_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if re.search("'", field.data):
            raise ValidationError('script cannot contain single quote')
        if re.search('\n', field.data):
            raise ValidationError('script cannot contain return')

    mnt_choices = []
    if os.environ.get('HOSTPATH_ENABLE') == '1':
        mnt_choice = os.environ.get('HOSTPATH_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('NFS_ENABLE') == '1':
        mnt_choice = os.environ.get('NFS_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('GLUSTER_ENABLE') == '1':
        mnt_choice = os.environ.get('GLUSTER_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('CEPH_ENABLE') == '1':
        mnt_choice = os.environ.get('CEPH_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    mnt_option = SelectField('Select Mnt Option:', choices=mnt_choices)
    name = StringField('Template Name: ', validators=[name_uniq_check])
    script = StringField('Bash Script:', validators = [cmd_format_check], widget=TextArea())
    image = StringField('Container Image:', validators = [DataRequired()])
    log_dir = StringField('Tensorboard Log Dir')
    mnt_option = SelectField('Select Mnt Option:', choices=mnt_choices)
    desc = StringField('Description: ')
    submit = SubmitField('Save')


class TemplatesEditForm(FlaskForm):
    def cmd_format_check(form, field):
        if not field.data:
            raise ValidationError('Name cannot be empty')
        if re.search("'", field.data):
            raise ValidationError('script cannot contain single quote')
        if re.search('\n', field.data):
            raise ValidationError('script cannot contain return')

    script = StringField('Bash Script:', validators = [cmd_format_check], widget=TextArea())
    image = StringField('Container Image:', validators = [DataRequired()])
    log_dir = StringField('Tensorboard Log Dir')
    mnt_choices = []
    if os.environ.get('HOSTPATH_ENABLE') == '1':
        mnt_choice = os.environ.get('HOSTPATH_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('NFS_ENABLE') == '1':
        mnt_choice = os.environ.get('NFS_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('GLUSTER_ENABLE') == '1':
        mnt_choice = os.environ.get('GLUSTER_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    if os.environ.get('CEPH_ENABLE') == '1':
        mnt_choice = os.environ.get('CEPH_CONTAINER')
        mnt_path = '/mnt/{}'.format(mnt_choice)
        display_choice = '{}: {}'.format(mnt_choice, mnt_path)
        mnt_choices.append([mnt_choice, display_choice])
    mnt_option = SelectField('Select Mnt Option:', choices=mnt_choices)
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
