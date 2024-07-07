import json
import requests
import hashlib
from datetime import datetime
from parsing_and_data.paring_data.db import tobd

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

def parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, dca, vid, rem, sd, room, balcon, typy):
    offset = 0
    try:
        for year in range(2024, 1950, -1):
            req = dca.get(count_url, params={
                "address": addresse,
                "deal_type": "sale",
                "category": "living",
                "window_view": vid,
                "offer_type": [sd],
                "renovation": rem,
                "rooms": room,  
                "build_year__gte": year,
                "build_year__lte": year,
                "wall_type": typy,
                "balconies": balcon
            })
                                            
            count_obj = json.loads(req.text)
            total = count_obj["pagination"]["total"]
            #print(count_obj['result'])
            print(f"finishing searching total args for: {year}")
            print(total)
            for offset in range(0, total, 1):
                res = dca.get(offers_url, params={
                                                        "address": addresse,
                                                        "deal_type": "sale",
                                                        "category": "living",
                                                        "offer_type": [sd],
                                                        "window_view": vid,
                                                        "offset": offset,
                                                        "limit": 20,
                                                        "rooms": room,
                                                        "build_year__gte": year,
                                                        "build_year__lte": year,
                                                        "wall_type": typy,
                                                        "renovation": rem,
                                                        "balconies": balcon, 
                                                    })
                print("RES:", res)
                offers_obj = json.loads(res.text)
                result_data = offers_obj["result"]
                items = result_data["items"]
                #print(items)
                for item in items:
                    address = item['address']
                    price = item['price_info']
                    house = item['house']
                    object_info = item['object_info']
                    description = item['description']
                    row = (
                                address['name'],
                                price['price'],
                                object_info['floor'],
                                house['floors'],
                                object_info['rooms'],
                                object_info['area'],
                                address['locality']['name'],
                                sd,
                                rem,
                                balcon,
                                address['guid'],
                                vid,
                                description,
                                year,)
                                #print(row)
                    tobd(row, database, user, password, host, port, tablename)                        
    except:
        print("error")
                #continue

def main_parser_fn(addresse, database, user, password, host, port, tablename):#, database, user, password, host, port):    
    #main params

    remont = ["standard", "design", "office_finishing", "simple", "required_cosmetic", "required_repair", "well_done", "without_repair"] #without_repair design standard well_done
    balcons = [1, 2]
    rooms = ["1", "st", "2", "3", "4"]
    type_dome = ["layout", "flat"] 
    wide_from_winow = ['garden', 'park', 'water', 'forest', 'street']
    perec = ["brick", "wood", "monolith", "panel", "block", "brick_monolith", "shield", "frame", "foamed_block", "gaz_block", "metal"]
    offers_url = "https://offers-service.domclick.ru/research/v5/offers/"
    count_url = "https://offers-service.domclick.ru/research/v5/offers/count/"
    for room in rooms:
        for vid in wide_from_winow:
            for type in perec:
                for balcon in balcons:
                    for sd in type_dome:
                        for rem in remont:
                            parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, DomClickApi(), vid, rem, sd, room, balcon, type)

    return 0                    
