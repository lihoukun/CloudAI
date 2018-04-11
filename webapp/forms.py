from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, IntegerField, SelectField, RadioField, SubmitField
from wtforms.validators import NumberRange, DataRequired, ValidationError


class TrainingsNewForm(FlaskForm):
    model_name = SelectField('Select Model: ')
    num_gpu = IntegerField('Number of GPU: ')
    num_cpu = IntegerField('Number of CPU: ')
    num_epoch = IntegerField('Number of Epoch: ', validators=[NumberRange(min=1)])
    train_option = RadioField('Train Option', choices = [('legacy', 'Continue from Existing Training'), ('new', 'Start a New Training')], default='new')
    train_label = SelectField('Training Label: ')
    submit = SubmitField('Train')

class EvalForm(FlaskForm):
    log_dir = SelectField('LOG Directory: ')
    submit = SubmitField('Start TensorBoard')

class SystemForm(FlaskForm):
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
