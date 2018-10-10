from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'exaairocks'

from flask import render_template, flash, redirect, request, url_for
from wtforms.validators import NumberRange

from forms import TrainingsNewForm, KubecmdForm, EvalForm, StopForm, ShowForm, ModelsNewForm, DeleteForm
from database import db_session
from models import TrainingModel, TemplateModel
from kube_parse import get_total_nodes, get_gpu_per_node
from subprocess import check_output
import re
import os
import datetime


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trainings/new/', methods=['GET', 'POST'])
def trainings_new():
    def gen_script(record_dir, script):
        if not os.path.isdir(record_dir):
            os.makedirs(record_dir, 0o775)
        filename = '{}/tensorflow.sh'.format(record_dir)
        with open(filename, 'w+') as f:
            f.write('set -x\n')
            f.write('umask 2\n')
            f.write(script)

    def transform_dir(container_dir):
        if os.environ.get('HOSTPATH_ENABLE') == '1' and container_dir.startswith(os.environ.get('HOSTPATH_CONTAINER')):
            return container_dir.replace(os.environ.get('HOSTPATH_CONTAINER'), os.environ.get('HOSTPATH_HOST'))
        elif os.environ.get('GLUSTER_ENABLE') == '1' and container_dir.startswith(os.environ.get('GLUSTER_CONTAINER')):
            return container_dir.replace(os.environ.get('GLUSTER_CONTAINER'), os.environ.get('GLUSTER_HOST'))
        elif os.environ.get('NFS_ENABLE') == '1' and container_dir.startswith(os.environ.get('NFS_CONTAINER')):
            return container_dir.replace(os.environ.get('NFS_CONTAINER'), os.environ.get('NFS_HOST'))
        else:
            return container_dir

    form = TrainingsNewForm()
    form.template_name.choices = [[t.name]*2 for t in TemplateModel.query.all()]
    form.num_gpu.validators=[NumberRange(min=1, max=get_total_nodes())]
    form.num_cpu.validators=[NumberRange(min=0, max=get_total_nodes())]
    if form.validate_on_submit():
        train_name = form.train_name.data
        template_name = form.template_name.data
        num_cpu = form.num_cpu.data
        num_gpu = form.num_gpu.data
        num_epoch = form.num_epoch.data
        result = TemplateModel.query.filter(name == template_name).first()
        script, image, log_dir, mnt_option = result.bash_script, result.image_dir, result.log_dir, result.mnt_option
        record_dir = '{}/train/{}/records'.format(os.environ['SHARED_HOST'], train_name)

        gen_script(record_dir, script)

        cmd = 'python3 {}/scripts/gen_k8s_yaml.py'.format(os.path.dirname(os.path.realpath(__file__)))
        cmd += ' --ps_num {} --worker_num {}'.format(num_cpu, num_gpu)
        cmd += ' --gpu_per_node {}'.format(get_gpu_per_node())
        cmd += ' --epoch {}'.format(num_epoch)
        cmd += ' --record_dir {}'.format(record_dir)
        cmd += ' --name {}'.format(train_name)
        cmd += ' --image {}'.format(image)
        print(cmd)
        os.system(cmd)

        t = TrainingModel(name=train_name, num_gpu=num_gpu, num_cpu=num_cpu, num_epoch=num_epoch, bash_script=script,
                          image_dir=image, log_dir=log_dir, mnt_option=mnt_option, email=form.mail_to.data, status='PEND')
        db_session.add(t)
        db_session.commit()
        return redirect(url_for('trainings', type='active'))

    return render_template('trainings_new.html', form=form)


@app.route('/trainings/<type>', methods=['GET', 'POST'])
def trainings(type='active'):
    data = []
    for t in TrainingModel.query.all():
        name, status, log_dir = t.name, t.status, t.log_dir
        if type == 'active' and status != 'STOPPED':
            data.append([name, status, log_dir])
        if type != 'active' and status == 'STOPPED':
            data.append([name, status, log_dir])

    return render_template('trainings.html', data=data, type=type)

@app.route('/training/<name>', methods=['GET', 'POST'])
def training(name=None, desc = [], log = []):
    data = []
    cmd = 'kubectl get pods -l name={}'.format(name)
    output = check_output(cmd.split()).decode('ascii')
    if output:
        for line in output.split('\n'):
            if line and line.strip():
                data.append(line.split()[:3])
        data.pop(0)

    forms = StopForm(prefix='forms')
    if forms.validate_on_submit():
        try:
            cmd = 'kubectl delete -f {}/train/{}/records/train.yaml'.format(os.environ['SHARED_HOST'], name)
            os.system(cmd)
            t = TrainingModel.query.filter(name=name).first()
            t.status = 'RUNNING'
            db_session.commit()
            update_training(label, 'RUNNING')
            flash('Training Label {} scheduled to stop'.format(name))
        except:
            flash('Failed to stop training label {}'.format(name))
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

    return render_template('training.html', name=name, data=data, forms=forms, formd=formd, forml=forml, desc=desc, log=log)


@app.route('/templates/new/', methods=['GET', 'POST'])
def templates_new():
    form = TemplatesNewForm()
    if form.validate_on_submit():

        t = TemplateModel(name=form.name.data, bash_script=form.script.data, image_dir=form.image.data,
                          log_dir=form.log_dir.data, mnt_option=form.mnt_option.data, description=form.desc.data)
        db_session.add(t)
        db_session.commit()
        return redirect(url_for('models'))

    return render_template('templates_new.html', form=form)


@app.route('/templates/')
def templates():
    data = []
    for t in TemplateModel.query.all():
        data.append((t.name, t.image_dir, t.description))
    return render_template('templates.html', data=data)


@app.route('/template/<name>', methods=['GET', 'POST'])
def template(name=None):
    t = TemplateModel.query.filter(name=name).first()
    data = [t.name, t.bash_script, t.image_dir, t.log_dir, t.mnt_option, t.description]

<<<<<<< HEAD
    form = DeleteForm()
    if formd.validate_on_submit():
=======
    form = ModelDeleteForm()
    if form.validate_on_submit():
>>>>>>> b5c74ab62027ef79c78cf8569e5e4ab53fc6105c
        delete_model(name)
        flash("model {} has been deleted".format(name))
        return redirect(url_for('templates'))
    return render_template('template.html', data=data, form=form)


@app.route('/eval/', methods=('GET', 'POST'))
def eval():
    for t in TrainingModel.query.filter(log_dir.isnot(None)).all():

    form = EvalForm()
    form.log_dir.choices = [(t.log_dir, t.name) for t in TrainingModel.query.filter(log_dir.isnot(None)).all()]
    if form.validate_on_submit():
        log_dir = form.log_dir.data
        custom_dir = form.custom_dir.data
        os.system("docker kill exaai-tensorboard")
        os.system("docker rm exaai-tensorboard")
        if custom_dir != '':
            cmd = "docker run --name exaai-tensorboard -d -p {0}:6006 -v {1}:/local/mnt/workspace".format(os.environ.get('TENSORBOARD_PORT'), custom_dir)
        else:
            cmd = "docker run --name exaai-tensorboard -d -p {0}:6006 -v {1}:/local/mnt/workspace".format(os.environ.get('TENSORBOARD_PORT'), log_dir)
        cmd +=" exaai/tensorboard tensorboard --logdir=/local/mnt/workspace"
        os.system(cmd)
        return redirect("http://tensorboard.{}".format(os.environ['NGROK_DOMAIN']))
    return render_template('eval.html', form=form, current=current)


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


@app.route('/notebook/', methods=('GET', 'POST'))
def notebook():
    return redirect("http://notebook.{}".format(os.environ['NGROK_DOMAIN']))


if __name__ == "__main__":
    app.run()
