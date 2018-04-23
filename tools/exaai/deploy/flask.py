import os
import sqlite3
from subprocess import Popen, check_output

def init_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("CREATE TABLE models (name string primary key, script text, description string)")
    c.execute("CREATE TABLE trainings (label string primary key, status string, train_dir string, tensorboard integer)")
    conn.commit()
    conn.close()

def deploy_web():
    db_file = os.path.dirname(os.path.realpath(__file__)) + '/../../../../../sqlite3.db'
    if not os.path.isfile(db_file):
        print("Database is not setup, setting up now")
        init_db(db_file)

    cmd = "ps -u ai u"
    res = check_output(cmd.split()).decode('ascii').split('\n')
    for line in res:
        if re.search('flask run', line):
            pid = line.split()[1]
            os.system('kill {}'.format(pid))
            print('Kill flask process with PID {}'.format(pid))

    cwd = os.getcwd()
    flask_dir = os.path.dirname(os.path.realpath(__file__)) + '/../../../webapp'
    os.chdir(flask_dir)
    cmd = 'python3 -m flask run --host=0.0.0.0 --port={}'.format(os.environ.get('FLASK_PORT'))
    Popen(cmd.split())
    os.chdir(cwd)
