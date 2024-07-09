import json
import requests
import hashlib
from bs4 import BeautifulSoup
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
    

def get_extra_data_god(dca, ui):
    res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
    soup = BeautifulSoup(res.content, 'html.parser')
    s = soup.findAll('section', class_="EBeSC")
    for d in s:
        f = d.find('span', class_="ffG_w")
        return f.text

def get_extra_data_balcon(dca, ui):
    res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
    soup = BeautifulSoup(res.content, 'html.parser')
    repair_item = soup.find('li', {'data-e2e-id': "Количество балконов"})
    repair_value = repair_item.find('span', {'class': 'ffG_w', 'data-e2e-id': 'Значение'}).text.strip()

    return repair_value

def get_guid_of_regione(regione) -> str:
    offers_url = 'https://geo-service.domclick.ru/research/api/v1/autocomplete/regions'
    dca = DomClickApi()
    res = dca.get(offers_url, params={
        "name": regione  #<<-- you regione str
    })
    count_obj = json.loads(res.text)
    print(count_obj['answer']['items'][0]['guid'])
    return count_obj['answer']['items'][0]['guid']

def parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, dca, vid, rem, room, balcon, typyc):
    offset = 0
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
                        row = (
                                    address['name'],
                                    price['price'],
                                    object_info['floor'],
                                    house['floors'],
                                    object_info['rooms'],
                                    object_info['area'],
                                    address['locality']['name'],
                                    'flat',
                                    rem,
                                    balcon,
                                    url,
                                    vid,
                                    '0',
                                    get_extra_data_god(DomClickApi(), url))
                        #print(row)
                        tobd(row, database, user, password, host, port, tablename)  
                        #print("add to db")                      
    except:
        #print("error")
        pass  #continue
    return total
def main_parser_fn(addresse, database, user, password, host, port, tablename):#, database, user, password, host, port):    
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
                            percents += parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, DomClickApi(), vid, rem, room, balcon, typec)
                            print('\rNAYDENO: {}'.format(percents), end='')
    return 0                    
