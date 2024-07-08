import psycopg2
from psycopg2 import *

def tobd(list, database, user, password, host, port, tablename):
    try:
        connection = psycopg2.connect(database=database,
                                        user=user,
                                        password=password,
                                        host=host, 
                                        port = port)  
            
        cursor = connection.cursor()
        
        insert_query = f"""INSERT INTO {tablename} (address, price, floor, total_floors, rooms, area, city, home_type, remont, balcon, url, view_window, description) VALUES {list}"""

        cursor.execute(insert_query)
        connection.commit()

    except (Exception, Error, OperationalError) as error:
        pass
    finally:
        if connection:
            cursor.close()
            connection.close()

    return 0
