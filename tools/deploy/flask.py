import os
import sqlite3
import re
from subprocess import Popen, check_output

def init_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("CREATE TABLE models (name string primary key, script text, description string)")
    c.execute("CREATE TABLE trainings (label string primary key, status string, train_dir string, tensorboard integer, submit_at text, start_at text, stop_at text, num_gpu integer)")
    conn.commit()
    conn.close()

def check_update():
    migration_base = os.path.dirname(os.path.realpath(__file__)) + '/migrations'
    start_script = None

    for script in reversed(os.listdir(migration_base)):
        if not re.search('.py$', script):
            continue
        ret = os.system('python3 {}/{} check'.format(migration_base, script))
        if ret == 0:
            break
        else:
            start_script = script

    start = False
    for script in os.listdir(migration_base):
        if not re.search('.py$', script):
            continue
        if script == start_script:
            start = True
        if start:
            cmd = 'python3 {}/{} apply'.format(migration_base, script)
            print(cmd)
            os.system(cmd)

def check_db():
    db_file = os.environ.get('FLASK_DB')
    if not os.path.isfile(db_file):
        print("Database is not setup, setting up now")
        print(db_file)
        init_db(db_file)
    check_update()

def stop_web():
    cmd = "ps -u ai u"
    res = check_output(cmd.split()).decode('ascii').split('\n')
    for line in res:
        if re.search('gunicorn', line):
            pid = line.split()[1]
            os.system('kill {}'.format(pid))
            print('Kill flask process with PID {}'.format(pid))

def start_web():
    check_db()

    cwd = os.getcwd()
    flask_dir = os.path.dirname(os.path.realpath(__file__)) + '/../../webapp'
    os.chdir(flask_dir)
    cmd = 'gunicorn main:app -b 0.0.0.0:{} -w 4'.format(os.environ.get('FLASK_PORT'))
    Popen(cmd.split())
    os.chdir(cwd)
