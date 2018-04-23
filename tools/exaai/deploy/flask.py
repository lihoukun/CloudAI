import os
import sqlite3
from subprocess import Popen

def init_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("CREATE TABLE models (name string primary key, script text, description string)")
    c.execute("CREATE TABLE trainings (label string primary key, status string, train_dir string, tensorboard integer)")
    conn.commit()
    conn.close()

def deploy_web():
    db_file = os.path.basename(os.path.realpath(__file__)) + '/../../../sqlite3.db'
    if not os.path.isfile(db_file):
        init_db(db_file)

    cwd = os.getcwd()
    flask_dir = os.path.basename(os.path.realpath(__file__)) + '/../../../webapp'
    os.chdir(flask_dir)
    cmd = 'python3 -m flask run --host=0.0.0.0 --port={}'.format(os.environ.get('FLASK_PORT'))
    Popen(cmd.split())
    os.chdir(cwd)
