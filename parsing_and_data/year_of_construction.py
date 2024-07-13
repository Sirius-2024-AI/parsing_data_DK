import json
from all_def import DomClickApi
import requests
import pandas as pd
from multiprocessing import *
from bs4 import BeautifulSoup
from queue import Queue
import traceback
from threading import Thread
from datetime import datetime
import numpy as np

dca = DomClickApi()

df = pd.read_csv(r"/parsing_and_data/paring_data/pc2.csv").drop(labels=["id"], axis=1)

def get_extra_data(ui):
    dca = DomClickApi()
    try:
        res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
        soup = BeautifulSoup(res.content, 'html.parser')
       
        p1 = soup.find('li', {'data-e2e-id': 'Год постройки'})
        year = p1.find('span', {'data-e2e-id': 'Значение'}).text if p1 else 0 

        p2 = soup.find('li', {'data-e2e-id': 'Тип фундамента'})
        fundament = p2.find('span', {'data-e2e-id': 'Значение'}).text if p2 else 0

        p3 = soup.find('li', {'data-e2e-id': 'Тип перекрытий'})
        type_perec = p3.find('span', {'data-e2e-id': 'Значение'}).text if p3 else 0

        p4 = soup.find('li', {'data-e2e-id': 'Горячее водоснабжение'})
        hot_water = p4.find('span', {'data-e2e-id': 'Значение'}).text if p4 else 0

        p5 = soup.find('li', {'data-e2e-id': 'Кухня'})
        kitchen = p5.find('span', {'data-e2e-id': 'Значение'}).text if p5 else 0
        return year, type_perec, hot_water, fundament, kitchen
    except:
        return 0,0,0,0,0 


print(get_extra_data(2058968711))

list_of_dataframes = np.array_split(df, 5)

def extra_data(i):
    for index, row in list_of_dataframes[i].iterrows():
        uid = row['uid']
        b, y, s, u, t = get_extra_data(uid)
        list_of_dataframes[i].loc[index, 'year'] = b
        list_of_dataframes[i].loc[index, 'type_perec'] = y
        list_of_dataframes[i].loc[index, 'hot_water'] = s
        list_of_dataframes[i].loc[index, 'fundament'] = u
        list_of_dataframes[i].loc[index, 'kitchen'] = t
        list_of_dataframes[i].to_csv(f"data_{i}.csv")


if __name__ == '__main__':
    processes = []
    for i in range(5):
        process = Process(target=extra_data, args=(i,))
        processes.append(process)
        process.start()

    # Wait jobs done
    for process in processes:
        process.join()