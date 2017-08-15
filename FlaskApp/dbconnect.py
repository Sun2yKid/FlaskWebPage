import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "mysqlpassword",
                           db = "pythonprogramming")
    c = conn.cursor()

    return c, conn
