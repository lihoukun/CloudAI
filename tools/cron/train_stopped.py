from utils import send_mail, conn_db

import datetime
import os
import sys


def main():
    train_base = sys.argv[1]
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conn_db()
    c = conn.cursor()
    c.execute("update trainings set stop_at = '{}' where stop_at is NULL and status = 'STOPPED'".format(cur_time))
    c.execute("SELECT label, stop_at from trainings where status='STOPPED' order by stop_at asc")
    results = c.fetchall()
    delete_num  = len(results) - 100
    if delete_num <= 0: return

    c.execute("SELECT label from trainings where status='STOPPED' order by stop_at asc limit {}".format(delete_num))
    for res in c.fetchall():
        label, = res
        train_dir = '{}/train/{}'.format(train_base, label)
        if os.path.isdir(train_dir):
            os.system('rm -rf {}'.format(train_dir))
        if os.path.isdir(train_dir):
            sub = 'train dir {} cannot be deleted'.format(train_dir)
            msg = 'as title'
            #send_mail(sub, msg)
        else:
            c.execute("DELETE from trainings where label = '{}'".format(label))

    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    main()
