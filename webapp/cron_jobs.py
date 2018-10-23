from database import db_session, TrainingModel
from kube_parse import get_avail_worker
import datetime
import os
import sys
import smtplib
from subprocess import check_output

def send_mail(sub, mail_to, msg):
    if not mail_to: return 0
    to = mail_to.split(',')
    if not to: return 1
    FROM = 'DoNotReply@exaai.io'

    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(to), sub, msg)

    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, to, message)
    server.quit()

def pending():
    t = TrainingModel.query.filter_by(status='PENDING').order_by('submit_at').first()
    if t:
        name, num_gpu, mail_to = t.name, t.num_gpu, t.email
        avail_nodes = get_avail_worker()
        if num_gpu > avail_nodes:
            return 0

        cfg_file = '{}/train.yaml'.format(t.record_dir)
        t.start_at = datetime.datetime.now()
        if os.path.isfile(cfg_file):
            cmd = 'kubectl apply -f {}'.format(cfg_file)
            os.system(cmd)
            t.status = 'RUNNING'
        else:
            os.system('rm -rf {}'.format(t.record_dir))
            db_session.delete(t)
            sub = 'cfg file not found'
            msg = 'No cfg file at {}, deleted'.format(cfg_file)
            send_mail(sub, mail_to, msg)

        db_session.commit()


def running():
    with open('/home/ai/workspace/CloudAI/webapp/t.txt', 'a+') as f:
        f.write('hello\n')
    for t in TrainingModel.query.filter_by(status='RUNNING').order_by('submit_at'):
        cmd = 'kubectl get pods -l name={}'.format(t.name)
        output = check_output(cmd.split()).decode('ascii')
        if output:
            cmd = 'kubectl get pods -l name={},job=worker'.format(t.name)
            output = check_output(cmd.split()).decode('ascii')
            if output:
                lines = output.split('\n')
                is_finished = True
                for line in lines[1:-1]:
                    items = line.split()
                    if len(items) != 5 or items[2] != 'Completed':
                        is_finished = False
                        break
                if is_finished: t.status = 'COMPLETED'
        else:
            t.status = 'KILLED'

        if t.status  != 'RUNNING':
            sub = 'Training {} COMPLETED'.format(t.name)
            msg = 'as title'
            send_mail(sub, t.email, msg)
            t.stop_at = datetime.datetime.now()
            db_session.commit()


def completed():
    for t in TrainingModel.query.filter_by(status='COMPLETED').order_by('stop_at'):
        cmd = 'kubectl get pods -l name={}'.format(t.name)
        output = check_output(cmd.split()).decode('ascii')
        if output:
            cfg_file = '{}/train.yaml'.format(t.record_dir)
            if os.path.isfile(cfg_file):
                cmd = 'kubectl delete -f {}'.format(cfg_file)
                os.system(cmd)
            else:
                sub = 'cfg file not found'
                msg = 'No cfg file at {}, please manual delete'.format(cfg_file)
                send_mail(sub, t.email, msg)

        t.status = 'ARCHIVED'
        db_session.commit()


if __name__ == '__main__':
    if sys.argv[1] == 'pending':
        pending()
    elif sys.argv[1] == 'running':
        running()
