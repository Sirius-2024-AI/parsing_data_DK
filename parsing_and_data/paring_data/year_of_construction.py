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
from math import ceil
import warnings 
warnings.filterwarnings("ignore")
import numpy as np

dca = DomClickApi()
df = pd.read_csv("moscow.csv").drop(labels=["id"], axis=1)

def get_extra_data(ui):
    dca = DomClickApi()
    res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
    soup = BeautifulSoup(res.content, 'html.parser')
    #material_wall = soup.find('li', {'data-e2e-id': 'Материал стен'}).find('span', {'data-e2e-id': 'Значение'}).text
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

def extra_data():
        cnt = 0
        for index, row in df.iterrows():
            cnt += 1
            uid = row['uid']
            b, y, s, u, t = get_extra_data(uid)
            df.loc[index, 'year'] = b
            df.loc[index, 'type_perec'] = y
            df.loc[index, 'hot_water'] = s
            df.loc[index, 'fundament'] = u
            df.loc[index, 'kitchen'] = t
            print("Working... ", str(cnt) + '/' + '11335', ' ', ceil((cnt*100) / 11335), "%", end='\r')
            
extra_data()
df.to_csv("final_data.csv")
print("\nSuccess!")