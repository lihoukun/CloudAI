from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'exaairocks'

from flask import render_template, flash, redirect, request, url_for
from wtforms.validators import NumberRange

from forms import TrainingsNewForm, KubecmdForm, EvalForm, StopForm, ShowForm, ModelsNewForm, ModelEditForm
from db_parse import get_models, new_model, update_model, get_trainings, new_training, update_training

from subprocess import check_output
import re
import os
import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trainings/new/', methods=['GET', 'POST'])
def trainings_new():
    def get_max_gpu():
        cmd = "kubectl describe nodes"
        try:
            res = check_output(cmd.split()).decode('ascii').split('\n')
        except:
            return 0
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
        try:
            res = check_output(cmd.split()).decode('ascii').split('\n')
            return len(res) - 1
        except:
            return 0

    def gen_script(record_dir, job, name):
        if not os.path.isdir(record_dir):
            os.makedirs(record_dir, 0o777)
        filename = '{}/{}.sh'.format(record_dir, job)
        with open(filename, 'w+') as f:
            f.write('set -x\n')
            f.write(get_models(name)[1])

    form = TrainingsNewForm()
    form.train_label.choices = [[train[0]]*2 for train in get_trainings('STOPPED')]
    form.model_name.choices = [[model[0]]*2 for model in get_models()]
    if not form.train_label.choices:
        form.train_label.choices = [('', '---')]
    form.num_gpu.validators=[NumberRange(min=0, max=get_max_gpu())]
    form.num_cpu.validators=[NumberRange(min=0, max=get_max_cpu())]
    if form.validate_on_submit():
        signature = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        train_dir = '/nfs/nvme/train/{}_{}'.format(form.model_name.data, signature)
        record_dir = '{}/records'.format(train_dir)
        gen_script(record_dir, 'ps', form.model_name.data)
        gen_script(record_dir, 'worker', form.model_name.data)
        cfg_file = '/nfs/nvme/train/{}_{}/records/train.yaml'.format(form.model_name.data, signature)

        cmd = 'python3 {}/scripts/gen_k8s_yaml.py'.format(os.path.dirname(os.path.realpath(__file__)))
        cmd += ' {} train'.format(form.model_name.data)
        cmd += ' --ps_num {} --worker_num {}'.format(form.num_cpu.data, form.num_gpu.data)
        cmd += ' --epoch {}'.format(form.num_epoch.data)
        cmd += ' --record_dir {}'.format(record_dir)
        cmd += ' --signature {}'.format(signature)
        os.system(cmd)

        cmd = 'kubectl apply -f {}'.format(cfg_file)
        os.system(cmd)

        script = get_models(form.model_name.data)[1]
        if re.match('TRAIN_DIR', script):
            new_training('{}_{}'.format(form.model_name.data, signature), train_dir)
        else:
            new_training('{}_{}'.format(form.model_name.data, signature), None)
        return redirect(url_for('training', label='{}_{}'.format(form.model_name.data, signature)))

    return render_template('trainings_new.html', form=form)

@app.route('/trainings/<type>', methods=['GET', 'POST'])
def trainings(type='active'):
    def update_status(label):
        yaml_file = '/nfs/nvme/train/{}/records/train.yaml'.format(label)
        if os.path.isfile(yaml_file):
            m = re.match('(\S+)_(\d+)$', label)
            model, signature = m.group(1), m.group(2)
            cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
            output = check_output(cmd.split()).decode('ascii')
            if output:
                cmd = 'kubectl get pods -l model={},signature=s{},job=worker'.format(model, signature)
                output = check_output(cmd.split()).decode('ascii')
                if output:
                    status = 'RUNNING'
                else:
                    status = 'FINISHED'
            else:
                status = 'STOPPED'
        else:
            status = 'STOPPED'
        update_training(label, status)
        return status

    data = []
    for training in get_trainings():
        label, status, train_dir = training
        if status != 'STOPPED':
            status = update_status(label)

        if type == 'active' and status != 'STOPPED':
            data.append([label, status, train_dir])
        if type != 'active' and status == 'STOPPED':
            data.append([label, status, train_dir])

    return render_template('trainings.html', data=data, type=type)

@app.route('/training/<label>', methods=['GET', 'POST'])
def training(label=None, desc = [], log = []):
    data = []
    m = re.match('(\S+)_(\d+)$', label)
    model, signature = m.group(1), m.group(2)
    cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
    output = check_output(cmd.split()).decode('ascii')
    if output:
        for line in output.split('\n'):
            if line and line.strip():
                data.append(line.split()[:3])
        data.pop(0)

    forms = StopForm(prefix='forms')
    if forms.validate_on_submit():
        try:
            cmd = 'kubectl delete -f /nfs/nvme/train/{}/records/train.yaml'.format(label)
        except:
            pass
        flash('Training Label {} stopped'.format(label))
        os.system(cmd)
        return redirect(url_for('trainings', type='active'))

    formd = ShowForm(prefix='formd')
    if formd.validate_on_submit():
        name = request.form['name']
        try:
            cmd = 'kubectl describe pod {}'.format(name)
            desc = check_output(cmd.split()).decode('ascii').split('\n')
        except:
            desc = ['Oops, getting errors while retrieving descriptions', 'Maybe the conainer is not ready or teminated?']
    forml = ShowForm(prefix='forml')
    if forml.validate_on_submit():
        name = request.form['name']
        cmd = 'kubectl logs {}'.format(name)
        try:
            log = check_output(cmd.split()).decode('ascii').split('\n')
        except:
            log = ['Oops, getting error while retrieving logs', 'Maybe the job is not ready or terminated?']

    return render_template('training.html', label=label, data=data, forms=forms, formd=formd, forml=forml, desc=desc, log=log)

@app.route('/models/new/', methods=['GET', 'POST'])
def models_new():
    form = ModelsNewForm()
    if form.validate_on_submit():
        new_model(form.model_name.data, form.script.data, form.desc.data)
        return redirect(url_for('models'))
    return render_template('models_new.html', form=form)

@app.route('/models/')
def models():
    return render_template('models.html', data=get_models())

@app.route('/model/<name>', methods=['GET', 'POST'])
def model(name=None):
    data = get_models(name)
    form = ModelEditForm()
    if form.validate_on_submit():
        update_model(name, form.script.data, form.desc.data)
        return redirect(url_for('models'))

    return render_template('model.html', data=data, form=form)

@app.route('/eval/', methods=('GET', 'POST'))
def eval():
    form = EvalForm()
    form.log_dir.choices = [[train]*2 for train in get_trainings()]
    if form.validate_on_submit():
        flash('Evaluation reuqest for log_dir {} submitted'.format(form.log_dir.data))
        return redirect('/')
    return render_template('eval.html', form=form)

@app.route('/monitor/', methods=('GET', 'POST'))
def monitor():
    command = 'kubectl -n kube-system get secret'
    try:
        results = check_output(command.split()).decode('ascii').split('\n')
    except:
        return render_template('monitor.html', token = None)

    for result in results:
        if not result: continue
        secret = result.split()[0]
        if re.match('admin-user', secret):
            command = 'kubectl -n kube-system describe secret {}'.format(secret)
            try:
                output = check_output(command.split()).decode('ascii').split('\n')
            except:
                output = None
            break

    return render_template('monitor.html', token = output)

@app.route('/serve/')
def serve():
    return  render_template('serve.html')

@app.route('/kubecmd/', methods=('GET', 'POST'))
def kubecmd(command = None, output=[]):
    form = KubecmdForm()
    if form.validate_on_submit():
        command = 'kubectl -n {} {} {}'.format(form.namespace.data, form.action.data, form.target.data)
        try:
            output = check_output(command.split()).decode('ascii').split('\n')
        except:
            flash('Invalid')
    return render_template('kubecmd.html', form=form, command=command, output=output)
