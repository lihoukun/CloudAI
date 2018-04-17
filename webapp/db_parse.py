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

if __name__ == "__main__":
    print(get_models())
