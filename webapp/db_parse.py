import sqlite3

def get_models(name = None):
    models = []
    conn = sqlite3.connect('sqlite3.db')
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
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    script = script.replace("'", "''")
    if desc:
        cmd = "INSERT INTO models (name, script, description) VALUES ('{}', '{}', '{}')".format(name, script, desc)
    else:
        cmd = "INSERT INTO models (name, script) VALUES ('{}', '{}', '{}')".format(name, script)

    print(cmd)
    c.execute(cmd)
    conn.commit()
    conn.close()

def update_model(name, script, desc):
    conn = sqlite3.connect('sqlite3.db')
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
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS trainings (label string primary key, status string, train_dir string)")

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

def new_training(label, train_dir):
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS trainings (label string primary key, status string, train_dir string)")
    if train_dir:
        cmd = "INSERT INTO trainings (label, status, train_dir) VALUES ('{}', 'RUNNING', '{}')".format(label, train_dir)
    else:
        cmd = "INSERT INTO trainings (label, status) VALUES ('{}', 'RUNNING')".format(label)
    print(cmd)
    c.execute(cmd)
    conn.commit()
    conn.close()

def update_training(label, status):
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS trainings (label string primary key, status string, train_dir string)")
    cmd = "UPDATE trainings set status = '{}' where label = '{}'".format(status, label)
    c.execute(cmd)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print(get_models())
