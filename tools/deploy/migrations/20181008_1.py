import sys
import os
import sqlite3

def conn_db():
    db_file = os.environ.get('FLASK_DB')
    conn = sqlite3.connect(db_file)
    return conn

def up_to_date():
    ret = 0
    conn = conn_db()
    c = conn.cursor()
    try:
        c.execute("select mnt_option from models where mnt_option is NULL")
    except:
        conn.close()
        return 1

    res =c.fetchall()
    if res:
        ret = 1

    try:
        c.execute("select log_dir from models")
    except:
        conn.close()
        return 1

    conn.close()
    return ret

def apply_update():
    ret = 0
    conn = conn_db()
    c = conn.cursor()
    
    cmd = "alter table models add column mnt_option string"
    print(cmd)
    c.execute(cmd)
    cmd = "update models set mnt_option = 'HOSTPATH' where mnt_option is NULL"
    print(cmd)
    c.execute(cmd)
    cmd = "alter table models add column log_dir string"
    print(cmd)
    c.execute(cmd)

    conn.commit()
    conn.close()
    return ret

def main():
    if sys.argv[1] == 'check':
        ret = up_to_date()
    elif sys.argv[1] == 'apply':
        ret = apply_update()
    exit(ret)

if __name__ == '__main__':
    main()
