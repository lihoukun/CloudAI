import smtplib
import sqlite3
from subprocess import check_output
import re

def send_mail(sub, msg):
    FROM = 'DoNotReply@exaai.io'
    TO = ['xiaojie.zhang@exaai.io', 'houkun.li@exaai.io']

    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), sub, msg)

    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, TO, message)
    server.quit()

def conn_db():
    db_file = '/home/ai/workspace/sqlite3.db'
    conn = sqlite3.connect(db_file)
    return conn

def get_idle_nodes():
    cmd = "kubectl get nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
        total_nodes = len(res) - 3
    except:
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
