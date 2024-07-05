import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', password='1234567890', host='192.168.194.89')

conn.close()