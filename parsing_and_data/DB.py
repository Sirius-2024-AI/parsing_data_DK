import psycopg2
from psycopg2 import Error
from CONFIG import *

def tobd(list):
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
        #print("y")
    except (Exception, Error) as error:
        print(error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            #print("y")
    #print("y")
    return 0