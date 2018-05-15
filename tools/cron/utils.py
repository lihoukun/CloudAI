import smtplib
import sqlite3

def send_mail(to, sub, msg):
    FROM = 'DoNotReply@exaai.io'

    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(to), sub, msg)

    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, to, message)
    server.quit()

def conn_db():
    db_file = '/home/ai/workspace/sqlite3.db'
    conn = sqlite3.connect(db_file)
    return conn
