from utils import send_mail, conn_db

import datetime
import re
from subprocess import check_output

def main():
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conn_db()
    c = conn.cursor()
    c.execute("update trainings set start_at = '{}' where start_at is NULL and status = 'RUNNING'".format(cur_time))
    c.execute("SELECT label, mail_to from trainings where status='RUNNING' order by submit_at asc")
    for res in c.fetchall():
        status = 'RUNNING'

        label, mail_to = res
        m = re.match('(\S+)_(\d+)$', label)
        model, signature = m.group(1), m.group(2)
        cmd = 'kubectl get pods -l model={},signature=s{}'.format(model, signature)
        output = check_output(cmd.split()).decode('ascii')
        if output:
            cmd = 'kubectl get pods -l model={},signature=s{},job=worker'.format(model, signature)
            output = check_output(cmd.split()).decode('ascii')
            if output:
                lines = output.split('\n')
                is_finished = True
                for line in lines[1:-1]:
                    items = line.split()
                    if len(items) != 5 or items[2] != 'Completed':
                        is_finished = False
                        break
                if is_finished: status = 'FINISHED'
        else:
            status = 'STOPPED'

        if status  != 'RUNNING':
            sub = 'label {} change status to {}'.format(label, status)
            msg = 'as title'
            send_mail(sub, mail_to, msg)
            c.execute("UPDATE trainings set status='{}', stop_at = '{}' where label = '{}'".format(status, cur_time, label))

    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    main()
