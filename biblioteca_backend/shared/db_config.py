import pymysql

def get_mysql_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Rj19841820??r",
        database="biblioteca",
        cursorclass=pymysql.cursors.DictCursor
    )
