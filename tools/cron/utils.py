import smtplib
import sqlite3
from subprocess import check_output
import re

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

def conn_db():
    db_file = '/home/ai/workspace/sqlite3.db'
    conn = sqlite3.connect(db_file)
    return conn

def is_taint(node):
    cmd = 'kubectl describe node {}'.format(node)
    try:
        res = check_output(cmd.split()).decode('ascii')
    except:
        return 0
    if re.search('NoSchedule', res):
        return 0
    else:
        return 1

def get_total_nodes():
    cmd = "kubectl get nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0

    total_nodes = 0
    for line in res:
        m = re.search('(\S+)\s+Ready\s+(\S+)', line)
        if m:
            if m.group(2) == 'master':
                if is_taint(m.group(1)):
                    total_nodes += 1
            else:
                total_nodes += 1
    return total_nodes

def get_idle_nodes():
    total_nodes = get_total_nodes()
    if total_nodes == 0:
        return 0

    cmd = "kubectl get pods"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    busy_nodes = 0
    for line in res:
       if re.search('-worker-', line):
           busy_nodes += 1

    return (total_nodes - busy_nodes)
