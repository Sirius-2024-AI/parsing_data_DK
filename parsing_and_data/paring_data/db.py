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

        insert_query = f"""INSERT INTO metro (address, price, floor, total_floors, rooms, area, city, home_type, remont, balcon, url, view_window, description, build_year) VALUES {list}"""

        cursor.execute(insert_query)
        connection.commit()

    except (Exception, Error, OperationalError) as error:
        print(error)
    finally:
        if connection:
            cursor.close()
            connection.close()

    return 0