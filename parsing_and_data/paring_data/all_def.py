import json
import requests
import hashlib
import pandas as pd
from multiprocessing import *
from queue import Queue
import traceback
from threading import Thread
from datetime import datetime

class DomClickApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-Service": "true",
                                    "Connection": "Keep-Alive",
                                     "User-Agent": "Android; 12; Google; google_pixel_5; 8.72.0; 8720006; ; NONAUTH"
                                     })

        # init (get cookies)
        self.get("https://api.domclick.ru/core/no-auth-zone/api/v1/ensure_session")
        self.get("https://ipoteka.domclick.ru/mobile/v1/feature_toggles")

    def get(self, url, **kwargs):
        try:
            self.__update_headers(url, **kwargs)
            result = self.session.get(url, **kwargs)
            #print(self.session.cookies.get_dict())
            return result
        except:
            pass

    def __update_headers(self, url, **kwargs):
        try:
            url = self.__get_prepared_url(url, **kwargs)
            sault = "ad65f331b02b90d868cbdd660d82aba0"
            timestamp = str(int(datetime.now().timestamp()))
            encoded = (sault + url + timestamp).encode("UTF-8")
            h = hashlib.md5(encoded).hexdigest()
            self.session.headers.update({"Timestamp": timestamp,
                                        "Hash": "v1:" + h,
                                        })
        except:
            pass

    def __get_prepared_url(self, url, **kwargs):
        p = requests.models.PreparedRequest()
        p.prepare(method="GET", url=url, **kwargs)
        return p.url
    

def get_guid_of_regione(regione) -> str:
    offers_url = 'https://geo-service.domclick.ru/research/api/v1/autocomplete/regions'
    dca = DomClickApi()
    res = dca.get(offers_url, params={
        "name": regione  #<<-- you regione str
    })
    count_obj = json.loads(res.text)
    print(count_obj['answer']['items'][0]['guid'])
    return count_obj['answer']['items'][0]['guid']

def parser(addresse, offers_url, count_url, dca, vid, rem, room, balcon, typyc, file):
    offset = 0
    dataset = []
    try:
            req = dca.get(count_url, params={
                "address": addresse,
                "deal_type": "sale",
                "category": "living",
                "window_view": vid,
                "offer_type": ['flat'],
                "renovation": rem,
                "rooms": room,  
                "wall_type": typyc,
                "balconies": balcon
            })
                                            
            count_obj = json.loads(req.text)
            total = count_obj["pagination"]["total"]
            #print(count_obj['result'])
            #print(total)
            for offset in range(0, total, 1):
                    res = dca.get(offers_url, params={
                                                            "address": addresse,
                                                            "deal_type": "sale",
                                                            "category": "living",
                                                            "offer_type": ['flat'],
                                                            "window_view": vid,
                                                            "offset": offset,
                                                            "limit": 1,
                                                            "rooms": room,
                                                            "wall_type": typyc,
                                                            "renovation": rem,
                                                            "balconies": balcon, 
                                                        })
                    #print("RES:", res)
                    offers_obj = json.loads(res.text)
                    result_data = offers_obj["result"]
                    items = result_data["items"]
                    
                    #print(items)
                    for item in items:
                        address = item['address']
                        price = item['price_info']
                        house = item['house']
                        url = item['id']
                        object_info = item['object_info']
                        row = {
                                "address": address['name'],
                                "price": price['price'],
                                "floor": object_info['floor'],
                                "house": house['floors'],
                                "rooms": object_info['rooms'],
                                "area": object_info['area'],
                                "name": address['locality']['name'],
                                "remont": rem,
                                "balcon": balcon,
                                "url": url,
                                "vid": vid,
                                
                        }
                        dataset.append(row)
                        #print(row)
                        #tobd(row, database, user, password, host, port, tablename)  
                        #print("add to db")
            df = pd.DataFrame(dataset)      
            df.to_csv(file, mode='a', header=False)       
    except Exception:
        print(traceback.format_exc())
        

def main_parser_fn(addresse, file):#, database, user, password, host, port):    
    #main params
    percents = 0
    remont = ["standard", "design", "office_finishing", "simple", "required_cosmetic", "required_repair", "well_done", "without_repair"] #without_repair design standard well_done
    balcons = [1, 2]
    rooms = ["1", "st", "2", "3", "4"]
    wide_from_winow = ['garden', 'park', 'water', 'forest', 'street']
    perec = ["brick", "wood", "monolith", "panel", "block", "brick_monolith", "shield", "frame", "foamed_block", "gaz_block", "metal"]
    offers_url = "https://offers-service.domclick.ru/research/v5/offers/"
    count_url = "https://offers-service.domclick.ru/research/v5/offers/count/"
    for room in rooms:
        for vid in wide_from_winow:
            for typec in perec:
                for balcon in balcons:
                        for rem in remont:
                            parser(addresse, offers_url, count_url, DomClickApi(), vid, rem, room, balcon, typec, file)
                            

