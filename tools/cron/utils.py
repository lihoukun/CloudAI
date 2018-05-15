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

def get_idle_gpu():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    max_gpu = 0
    flip = False
    for line in res:
        m = re.search('gpu:\s+(\d)', line)
        if m:
            if flip:
                max_gpu += int(m.group(1))
                flip = False
            else:
                flip = True

    cmd = "kubectl get pods"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    busy_gpu = 0
    for line in res:
       if re.search('-worker-', line):
           busy_gpu += 1

    return (max_gpu - busy_gpu)
