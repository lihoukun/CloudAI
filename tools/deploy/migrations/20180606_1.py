import sys

def conn_db():
    db_file = os.environ.get('FLASK_DB')
    conn = sqlite3.connect(db_file)
    return conn

def need_update():
    return False

def apply_update():
    return 0

def main():
    if sys.argv[1] == 'check':
        return need_update()
    elif sys.argv[1] == 'apply':
        return apply_update()
    else:
        if need_update():
            return apply_update()
        else:
            return 0

if __name__ == '__main__':
    main()

