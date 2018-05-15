from utils import send_mail, conn_db

def main():
    conn = conn_db()
    c = conn.cursor()
    c.execute("select * from trainings")
    results = c.fetchall()
    for result in results:
        print(result)

if __name__ == '__main__':
    main()
