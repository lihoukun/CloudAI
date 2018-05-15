from utils import send_mail, conn_db, get_idle_gpu

import datetime
import os
import re

def main():
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conn_db()
    c = conn.cursor()
    c.execute("SELECT label, num_gpu from trainings where status='PEND' order by submit_at asc limit 1")
    res = c.fetchone()
    if res:
        label, num_gpu = res
        if num_gpu < get_idle_gpu(): return 0

        m = re.match('(\S+)_(\d+)$', label)
        model, signature = m.group(1), m.group(2)
        cfg_file = '/nfs/gdv/train/{}_{}/records/train.yaml'.format(model, signature)
        if os.path.isfile(cfg_file):
            cmd = 'kubectl apply -f {}'.format(cfg_file)
            os.system(cmd)
            c.execute("UPDATE trainings set status='RUNNING', start_at = '{}' where label = '{}'".format(cur_time, label))
        else:
            c.execute("UPDATE trainings set status='STOPPED', start_at = '{0}', stop_at = '{0}' where label = '{1}'".format(cur_time, label))
            to = ["houkun.li@exaai.io", "xiaojie.zhang@exaai.io"]
            sub = 'cfg file not found'
            msg = 'No cfg file at {}, deleted'.format(cfg_file)
            send_mail(to, sub, msg)

    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    main()
