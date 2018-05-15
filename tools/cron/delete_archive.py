from utils import send_mail, conn_db

import datetime

def main():
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conn_db()
    c = conn.cursor()
    #c.execute("alter table trainings add column stop_at text")
    #c.execute("update trainings set stop_at = '{}' where stop_at is null".format(cur_time))
    c.execute("select * from trainings")
    res = c.fetchall()[0]
    print(res)
    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    main()
