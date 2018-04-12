from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'exaairocks'

from flask import render_template, flash, redirect, request
from wtforms.validators import NumberRange

from forms import TrainingsNewForm, SystemForm, EvalForm, TrainingsForm
from dir_parse import get_models, get_trainings

from subprocess import check_output
import re
import os
import datetime

@app.route('/')
def index():
    sysform = SystemForm()
    if sysform.validate_on_submit():
        pass
    return render_template('index.html')

@app.route('/trainings/new/', methods=['GET', 'POST'])
def trainings_new():
    def get_max_gpu():
        cmd = "kubectl describe nodes"
        res = check_output(cmd.split(' ')).decode('ascii').split('\n')
        is_avail = 0
        max_gpu = 0
        for line in res:
            if re.search('gpu:', line):
                if is_avail:
                    max_gpu += 1
                    is_avail = 0
                else:
                    is_avail = 1
        return max_gpu

    def get_max_cpu():
        cmd = "kubectl get nodes"
        res = check_output(cmd.split(' ')).decode('ascii').split('\n')
        return len(res) - 1

    form = TrainingsNewForm()
    form.train_label.choices = [[train]*2 for train in get_trainings()]
    form.model_name.choices = [[model[0]]*2 for model in get_models()]
    if not form.train_label.choices:
        form.train_label.choices = [('', '---')]
    form.num_gpu.validators=[NumberRange(min=1, max=get_max_gpu())]
    form.num_cpu.validators=[NumberRange(min=1, max=get_max_cpu())]
    if form.validate_on_submit():
        signature = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        cfg_file = '/data/train/{}_{}/records/train.yaml'.format(form.model_name.data, signature)

        cmd = 'python36 {}/scripts/gen_k8s_yaml.py'.format(os.path.dirname(os.path.realpath(__file__)))
        cmd += ' {} train'.format(form.model_name.data)
        cmd += ' --ps_num {} --worker_num {}'.format(form.num_cpu.data, form.num_gpu.data)
        cmd += ' --epoch {}'.format(form.num_epoch.data)
        cmd += ' --out_file {}'.format(cfg_file)
        cmd += ' --signature {}'.format(signature)
        flash(cmd)
        os.system(cmd)

        cmd = 'kubectl apply -f {}'.format(cfg_file)
        flash(cmd)
        os.system(cmd)
        return redirect('/')
    return render_template('trainings_new.html', form=form)

@app.route('/trainings/', methods=['GET', 'POST'])
def trainings():
    def get_status(training):
        yaml_file = '/data/train/{}/records/train.yaml'.format(training)
        if not os.path.isfile(yaml_file): return 'STOPPED'

        model, signature = training.split('_')
        cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
        output = check_output(cmd.split(' ')).decode('ascii')
        if not output: return 'STOPPED'


        cmd = 'kubectl get pods -l model={},signature=s{},job=worker'.format(model, signature)
        output = check_output(cmd.split(' ')).decode('ascii')
        if not output: return 'FINISHED'
        return 'RUNNING'

    data = []
    for training in get_trainings():
        status = get_status(training)
        data.append([training, status])

    form = TrainingsForm()
    form.train_label.choices = [[row[0]]*2 for row in data]
    if form.validate_on_submit():
        if form.train_label.data:
            flash('Training Label {} picked'.format(form.train_label.data))

    return render_template('trainings.html', data=data)

@app.route('/training/<label>', methods=['GET', 'POST'])
def training(label):
    data = []
    model, signature = label.split('_')
    cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
    output = check_output(cmd.split(' ')).decode('ascii')
    if output:
        for line in output.split('\n'):
            data.append(line.split())

    return render_template('training.html', label=label, data=data, form=form)

@app.route('/models/')
def models():
    return render_template('models.html', data=get_models())

@app.route('/eval/', methods=('GET', 'POST'))
def eval():
    form = EvalForm()
    form.log_dir.choices = [[train]*2 for train in get_trainings()]
    if form.validate_on_submit():
        flash('Evaluation reuqest for log_dir {} submitted'.format(form.log_dir.data))
        return redirect('/')
    return render_template('eval.html', form=form)

@app.route('/serve/')
def serve():
    return  render_template('serve.html')

@app.route('/kubecmd/', methods=('GET', 'POST'))
def kubecmd(command = None, output=[]):
    form = SystemForm()
    if form.validate_on_submit():
        command = 'kubectl {} -l {}'.format(form.action.data, form.label_str.data)
        try:
            output = check_output(command.split(' ')).decode('ascii').split('\n')
        except:
            flash('Invalid')
    return render_template('kubecmd.html', form=form, command=command, output=output)