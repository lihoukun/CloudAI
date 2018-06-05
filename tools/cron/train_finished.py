from utils import send_mail, conn_db

import datetime
import re
import os
from subprocess import check_output

def main():
    train_base = sys.argv[1]
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conn_db()
    c = conn.cursor()
    c.execute("update trainings set stop_at = '{}' where stop_at is NULL and status = 'FINISHED'".format(cur_time))
    c.execute("SELECT label from trainings where status='FINISHED' order by stop_at asc")
    for res in c.fetchall():
        label, = res
        m = re.match('(\S+)_(\d+)$', label)
        model, signature = m.group(1), m.group(2)

        cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
        output = check_output(cmd.split()).decode('ascii')
        if output:
            cfg_file = '{}/train/{}_{}/records/train.yaml'.format(train_base, model, signature)
            if os.path.isfile(cfg_file):
                cmd = 'kubectl delete -f {}'.format(cfg_file)
                os.system(cmd)
            else:
                sub = 'cfg file not found'
                msg = 'No cfg file at {}, please manual delete'.format(cfg_file)
                send_mail(sub, msg)
        else:
            status = 'STOPPED'
            c.execute("UPDATE trainings set status='{}' where label = '{}'".format(status, label))

    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    main()
