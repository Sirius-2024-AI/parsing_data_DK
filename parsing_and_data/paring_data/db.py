import psycopg2
from psycopg2 import *

def tobd(list, database, user, password, host, port):
    try:
        connection = psycopg2.connect(database=database,
                                        user=user,
                                        password=password,
                                        host=host, 
                                        port = port)  
            
        cursor = connection.cursor()

        insert_query = f"""INSERT INTO datasets (address_name, price, square_price, floors, rooms, area, city, type_home, remont, balcon, url) VALUES {list}"""

        cursor.execute(insert_query)
        connection.commit()

    except (Exception, Error, OperationalError) as error:
        print(error)
    finally:
        if connection:
            cursor.close()
            connection.close()

    return 0