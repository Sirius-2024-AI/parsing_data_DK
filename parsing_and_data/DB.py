import psycopg2
from psycopg2 import Error

def tobd(list):
    try:
        connection = psycopg2.connect(database='',
                                    user='',
                                    password='',
                                    host='', 
                                    port = 0)  
        
        cursor = connection.cursor()

        insert_query = f"""INSERT INTO datasets (address_name, price, square_price, floors, rooms, area, local, type_home, remont, balcon) VALUES {list}"""

        cursor.execute(insert_query)
        connection.commit()
    except (Exception, Error) as error:
        return 1
    finally:
        if connection:
            cursor.close()
            connection.close()

    return 0