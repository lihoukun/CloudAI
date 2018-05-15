import sqlite3
import os
import datetime

def get_conn():
    conn = sqlite3.connect(os.environ.get('FLASK_DB'))
    return conn

def get_models(name = None):
    models = []
    conn = get_conn()
    c = conn.cursor()

    if name:
        c.execute("SELECT name, script, description FROM models WHERE name = '{}'".format(name))
        name, script, desc = c.fetchone()
        script = script.replace("''", "'").replace('\r\n', '\n')
        models.append(name)
        models.append(script)
        models.append(desc)
    else:
        c.execute("SELECT name, script, description FROM models ORDER BY name")
        for res in c.fetchall():
            name, script, desc =  res
            script = script.replace("''", "'").replace('\r\n', '\n')
            models.append([name, script, desc])
    conn.close()
    return models

def new_model(name, script, desc):
    conn = get_conn()
    c = conn.cursor()
    script = script.replace("'", "''")
    if desc:
        cmd = "INSERT INTO models (name, script, description) VALUES ('{}', '{}', '{}')".format(name, script, desc)
    else:
        cmd = "INSERT INTO models (name, script) VALUES ('{}', '{}')".format(name, script)

    print(cmd)
    c.execute(cmd)
    conn.commit()
    conn.close()

def update_model(name, script, desc):
    conn = get_conn()
    c = conn.cursor()
    script = script.replace("'", "''")
    if desc:
        cmd = "UPDATE models SET script = '{}', description = '{}' WHERE name = '{}'".format(script, desc, name)
    else:
        cmd = "UPDATE models SET script = '{}' WHERE name = '{}'".format(script, name)
    print(cmd)
    c.execute(cmd)
    conn.commit()
    conn.close()

def get_trainings(status = None):
    trainings = []
    conn = get_conn()
    c = conn.cursor()

    cmd = "SELECT label, status, train_dir FROM trainings"
    if status:
        cmd += " WHERE status = '{}'".format(status)
    cmd += " ORDER by label"

    c.execute(cmd)
    for res in c.fetchall():
        label, status, train_dir = res
        trainings.append([label, status, train_dir])
    conn.close()
    return trainings

def get_tb_training():
    conn = get_conn()
    c = conn.cursor()

    cmd = "SELECT label, status, train_dir FROM trainings WHERE tensorboard = 1"
    c.execute(cmd)
    res = c.fetchone()
    return res

def update_tb_training(log_dir):
    conn = get_conn()
    c = conn.cursor()

    cmd = "UPDATE trainings set tensorboard = 0"
    c.execute(cmd)
    cmd = "UPDATE trainings set tensorboard = 1 WHERE train_dir = '{}'".format(log_dir)
    c.execute(cmd)
    conn.commit()
    conn.close()

def new_training(label,num_gpu, train_dir):
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    c = conn.cursor()
    cmd = "SELECT * FROM trainings where label = '{}'".format(label)
    c.execute(cmd)
    res = c.fetchone()
    if res:
        cmd = "UPDATE trainings set status = 'PEND', num_gpu = {} submit_at = '{}', ".format(cur_time, num_gpu)
        if train_dir:
            cmd += " train_dir = '{}' ".format(train_dir)
        else:
            cmd += " train_dir = NULL ".format(train_dir)
        cmd += " where label = '{}'".format(label)
        c.execute(cmd)
    else:
        cmd = "INSERT INTO trainings (label, status, submit_at, num_gpu) VALUES ('{}', 'PEND', '{}', {})".format(label, cur_time, num_gpu)
        c.execute(cmd)
        if train_dir:
            cmd = "UPDATE trainings set train_dir = '{}' WHERE label = '{}'".format(train_dir, label)
            c.execute(cmd)
    conn.commit()
    conn.close()

def update_training(label, status):
    conn = get_conn()
    c = conn.cursor()
    cmd = "UPDATE trainings set status = '{}' where label = '{}'".format(status, label)
    c.execute(cmd)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    conn = get_conn()
    c = conn.cursor()
    c.execute("select train_dir from trainings where train_dir is not null")
    for line in c.fetchall():
        print(line)

    conn.commit()
    conn.close()
