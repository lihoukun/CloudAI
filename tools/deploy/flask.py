import os
import re
from subprocess import Popen, check_output


def check_db():
    db_file = os.environ.get('FLASK_DB')
    if not os.path.isfile(db_file):
        print("Database is not setup, setting up now")
        print(db_file)
        os.chdir(os.path.dirname(os.path.abspath(db_file)))
        cmd = 'python3 database.py'
        os.system(cmd)


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
