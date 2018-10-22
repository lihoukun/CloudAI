from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'exaairocks'

from flask import render_template, flash, redirect, request, url_for
from wtforms.validators import NumberRange

from forms import TrainingsNewForm, TrainingResumeForm
from forms import KubecmdForm, EvalForm, StopForm, ShowForm, DeleteForm
from forms import TemplatesNewForm, TemplatesEditForm
from database import db_session
from database import TrainingModel, TemplateModel
from kube_parse import get_total_nodes, get_gpu_per_node
from subprocess import check_output
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
        params = form.params.data
        result = TemplateModel.query.filter_by(name=template_name).first()
        script, image, log_dir, mnt_option = result.bash_script, result.image_dir, result.log_dir, result.mnt_option
        record_dir = '{}/records/{}'.format(os.environ['SHARED_HOST'], train_name)

        cmd = 'python3 {}/scripts/gen_k8s_yaml.py'.format(os.path.dirname(os.path.realpath(__file__)))
        cmd += ' --ps_num {} --worker_num {}'.format(num_cpu, num_gpu)
        cmd += ' --gpu_per_node {}'.format(get_gpu_per_node())
        cmd += ' --epoch {}'.format(num_epoch)
        cmd += ' --record_dir {}'.format(record_dir)
        cmd += ' --name {}'.format(train_name)
        cmd += ' --image {}'.format(image)
        cmd += ' --mnt {}'.format(mnt_option)
        cmd += " --script '{}'".format(script)
        cmd += ' --params {}'.format(params)
        print(cmd)
        os.system(cmd)

        t = TrainingModel(name=train_name, num_gpu=num_gpu, num_cpu=num_cpu, num_epoch=num_epoch, bash_script=script,
                          image_dir=image, log_dir=log_dir, record_dir=record_dir, mnt_option=mnt_option,
                          email=form.mail_to.data, status='PENDING', params=params)
        db_session.add(t)
        db_session.commit()
        return redirect(url_for('trainings', type='active'))

    return render_template('trainings_new.html', form=form)


@app.route('/trainings/<type>', methods=['GET', 'POST'])
def trainings(type='active'):
    data = []
    for t in TrainingModel.query.all():
        data.append([t.name, t.status, t.num_gpu])

    return render_template('trainings.html', data=data, type=type)


@app.route('/training/config/<name>', methods=['GET', 'POST'])
def training_cfg(name=None):
    t = TrainingModel.query.filter_by(name=name).first()
    data = [name, t.status, t.num_gpu, t.num_cpu, t.num_epoch, t.email,
            t.bash_script, t.image_dir, t.log_dir, t.mnt_option, t.params]

    form = TrainingResumeForm()
    form.num_gpu.validators=[NumberRange(min=1, max=get_total_nodes())]
    form.num_cpu.validators=[NumberRange(min=0, max=get_total_nodes())]
    if form.validate_on_submit():
        num_cpu = form.num_cpu.data
        num_gpu = form.num_gpu.data
        num_epoch = form.num_epoch.data
        params = form.params.data
        email = form.mail_to.data

        cmd = 'kubectl delete -f {}/train.yaml'.format(t.record_dir)
        os.system(cmd)

        cmd = 'python3 {}/scripts/gen_k8s_yaml.py'.format(os.path.dirname(os.path.realpath(__file__)))
        cmd += ' --ps_num {} --worker_num {}'.format(num_cpu, num_gpu)
        cmd += ' --gpu_per_node {}'.format(get_gpu_per_node())
        cmd += ' --epoch {}'.format(num_epoch)
        cmd += ' --record_dir {}'.format(t.record_dir)
        cmd += ' --name {}'.format(name)
        cmd += ' --image {}'.format(t.image_dir)
        cmd += ' --mnt {}'.format(t.mnt_option)
        cmd += " --script '{}'".format(t.bash_script)
        cmd += ' --params {}'.format(params)
        print(cmd)
        os.system(cmd)

        t.num_cpu = num_cpu
        t.num_gpu = num_gpu
        t.num_epoch = num_epoch
        t.email = email
        t.status = 'PENDING'
        t.submit_at = datetime.datetime.now()
        t.start_at = None
        t.stop_at = None
        db_session.commit()
        return redirect(url_for('trainings', type='active'))

    return render_template('training_cfg.html', form=form, data=data)


@app.route('/training/info/<name>', methods=['GET', 'POST'])
def training_info(name=None, desc = [], log = []):
    data = []
    cmd = 'kubectl get pods -l name={}'.format(name)
    output = check_output(cmd.split()).decode('ascii')
    if output:
        for line in output.split('\n'):
            if line and line.strip():
                data.append(line.split()[:3])
        data.pop(0)

    t = TrainingModel.query.filter_by(name=name).first()
    if t.status == 'KILLED':
        forms = DeleteForm(prefix='forms')
        if forms.validate_on_submit():
            try:
                cmd = 'rm -rf {}'.format(t.record_dir)
                os.system(cmd)
                db_session.delete(t)
                db_session.commit()
                flash('Training {} deleted'.format(name))
            except:
                flash('Failed to delete training {}'.format(name))
            return redirect(url_for('trainings', type='active'))
    else:
        forms = StopForm(prefix='forms')
        if forms.validate_on_submit():
            try:
                cmd = 'kubectl delete -f {}/train.yaml'.format(t.record_dir)
                os.system(cmd)
                t.status = 'KILLED'
                db_session.commit()
                flash('Training {} killed'.format(name))
            except:
                flash('Failed to kill training {}'.format(name))
            return redirect(url_for('trainings', type='active'))

    formi = ShowForm(prefix='formi')
    if formi.validate_on_submit():
        name = request.form['name']
        try:
            cmd = 'kubectl describe pod {}'.format(name)
            desc = check_output(cmd.split()).decode('ascii').split('\n')
        except:
            desc = ['Oops, getting errors while retrieving descriptions',
                    'Maybe the conainer is not ready or teminated?']
    forml = ShowForm(prefix='forml')
    if forml.validate_on_submit():
        name = request.form['name']
        cmd = 'kubectl logs {}'.format(name)
        try:
            log = check_output(cmd.split()).decode('ascii').split('\n')
        except:
            log = ['Oops, getting error while retrieving logs', 'Maybe the job is not ready or terminated?']

    return render_template('training_info.html', name=name, data=data, forms=forms, formi=formi, forml=forml, desc=desc, log=log)


@app.route('/templates/new/', methods=['GET', 'POST'])
def templates_new():
    form = TemplatesNewForm()
    if form.validate_on_submit():

        t = TemplateModel(name=form.name.data, bash_script=form.script.data, image_dir=form.image.data,
                          log_dir=form.log_dir.data, mnt_option=form.mnt_option.data, description=form.desc.data)
        db_session.add(t)
        db_session.commit()
        return redirect(url_for('templates'))

    return render_template('templates_new.html', form=form)


@app.route('/templates/')
def templates():
    data = []
    for t in TemplateModel.query.all():
        data.append((t.name, t.image_dir, t.description))
    return render_template('templates.html', data=data)


@app.route('/template/<name>', methods=['GET', 'POST'])
def template(name=None):
    t = TemplateModel.query.filter_by(name=name).first()
    data = [t.name, t.bash_script, t.image_dir, t.log_dir, t.mnt_option, t.description]

    formu = TemplatesEditForm(mnt_option=t.mnt_option, prefix='formu')
    if formu.validate_on_submit():
        t.bash_script = formu.script.data
        t.image_dir = formu.image.data
        t.log_dir = formu.log_dir.data
        t.mnt_option = formu.mnt_option.data
        t.description = formu.desc.data

        db_session.commit()
        flash("template {} has been updated".format(name))
        return redirect(url_for('templates'))

    formd = DeleteForm(prefix='formd')
    if formd.validate_on_submit():
        db_session.delete(t)
        db_session.commit()
        flash("template {} has been deleted".format(name))
        return redirect(url_for('templates'))
    return render_template('template.html', data=data, formd=formd, formu=formu)


@app.route('/tensorboard/', methods=('GET', 'POST'))
def tensorboard():
    form = EvalForm()
    choices = []
    for t in TrainingModel.query.filter(TrainingModel.log_dir.isnot(None)).all():
        if t.log_dir:
            if t.mnt_option == 'hostpath':
                log_dir = t.log_dir.replace('/mnt/hostpath', os.environ.get('HOSTPATH_HOST'))
            elif t.mnt_option == 'gluster':
                log_dir = t.log_dir.replace('/mnt/gluster', os.environ.get('GLUSTER_HOST'))
            elif t.mnt_option == 'nfs':
                log_dir = t.log_dir.replace('/mnt/nfs', os.environ.get('NFS_HOST'))
            elif t.mnt_option == 'cephfs':
                log_dir = t.log_dir.replace('/mnt/cephfs', os.environ.get('CEPH_HOST'))
            choices.append((log_dir, t.name))
    if not choices:
        choices.append(('--', '--'))
    form.log_dir.choices = choices
    if form.validate_on_submit():
        log_dir = form.log_dir.data
        custom_dir = form.custom_dir.data
        os.system("docker kill exaai-tensorboard")
        os.system("docker rm exaai-tensorboard")
        if custom_dir != '':
            cmd = "docker run --name exaai-tensorboard -d -p {0}:6006 -v {1}:/local/mnt/workspace".format(os.environ.get('TENSORBOARD_PORT'), custom_dir)
        elif choices[0][0] == '--':
            flash('No tensorboard dir chosen')
            return render_template('tensorboard.html', form=form)
        else:
            cmd = "docker run --name exaai-tensorboard -d -p {0}:6006 -v {1}:/local/mnt/workspace".format(os.environ.get('TENSORBOARD_PORT'), log_dir)
        cmd +=" exaai/tensorboard tensorboard --logdir=/local/mnt/workspace"
        os.system(cmd)
        return redirect("http://tensorboard.{}".format(os.environ['NGROK_DOMAIN']))
    return render_template('tensorboard.html', form=form)


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
