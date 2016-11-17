import MySQLdb


def connection():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="text_passwords")
    c = conn.cursor()

    return c, conn
