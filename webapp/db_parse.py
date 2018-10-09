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
        c.execute("SELECT name, script, image, log_dir, mnt_option, description FROM models WHERE name = '{}'".format(name))
        name, script, image, log_dir, mnt_option, desc = c.fetchone()
        script = script.replace("''", "'").replace('\r\n', '\n')
        models.append(name)
        models.append(script)
        models.append(image)
        models.append(log_dir)
        models.append(mnt_option)
        models.append(desc)
    else:
        c.execute("SELECT name, script, image, log_dir, mnt_option, description FROM models ORDER BY name")
        for res in c.fetchall():
            name, script, image, log_dir, mnt_option, desc =  res
            script = script.replace("''", "'").replace('\r\n', '\n')
            models.append([name, script, image, log_dir, mnt_option, desc])
    conn.close()
    return models

def new_model(name, script, image, log_dir, mnt_option, desc):
    conn = get_conn()
    c = conn.cursor()
    script = script.replace("'", "''")
    cmd = "INSERT INTO models (name, script, image, mnt_option) VALUES ('{}', '{}', '{}', '{}')".format(name, script, image, mnt_option)
    print(cmd)
    c.execute(cmd)

    if desc:
        cmd = "UPDATE models set description = '{}' where name = '{}' ".format(desc, name)
        print(cmd)
        c.execute(cmd)

    if log_dir:
        cmd = "UPDATE models set log_dir = '{}' where name = '{}'".format(log_dir, name)
        print(cmd)
        c.execute(cmd)

    conn.commit()
    conn.close()

def update_model(name, script, image, desc):
    conn = get_conn()
    c = conn.cursor()
    script = script.replace("'", "''")
    if desc:
        cmd = "UPDATE models SET script = '{}', image = '{}', description = '{}' WHERE name = '{}'".format(script, image, desc, name)
    else:
        cmd = "UPDATE models SET script = '{}', image = '{}'  WHERE name = '{}'".format(script, image, name)
    print(cmd)
    c.execute(cmd)
    conn.commit()
    conn.close()

def delete_model(name):
    conn = get_conn()
    c = conn.cursor()
    cmd = "DELETE from models where name = '{}'".format(name)
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
    if log_dir != '':
        cmd = "UPDATE trainings set tensorboard = 1 WHERE train_dir = '{}'".format(log_dir)
        c.execute(cmd)
    conn.commit()
    conn.close()

def new_training(label, num_gpu, mail_to):
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    c = conn.cursor()
    cmd = "SELECT * FROM trainings where label = '{}'".format(label)
    c.execute(cmd)
    res = c.fetchone()
    if res:
        cmd = "UPDATE trainings set status = 'PEND', num_gpu = {}, submit_at = '{}' where label = '{}' ".format(num_gpu, cur_time,label)
        print(cmd)
        c.execute(cmd)
    else:
        cmd = "INSERT INTO trainings (label, status, submit_at, num_gpu) VALUES ('{}', 'PEND', '{}', {})".format(label, cur_time, num_gpu)
        c.execute(cmd)
    if mail_to:
        cmd = "UPDATE trainings set mail_to = '{}' WHERE label = '{}'".format(mail_to, label)
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
