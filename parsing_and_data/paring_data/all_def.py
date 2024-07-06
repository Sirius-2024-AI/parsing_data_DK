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
        self.__update_headers(url, **kwargs)
        result = self.session.get(url, **kwargs)
        #print(self.session.cookies.get_dict())
        return result

    def __update_headers(self, url, **kwargs):
        url = self.__get_prepared_url(url, **kwargs)
        sault = "ad65f331b02b90d868cbdd660d82aba0"
        timestamp = str(int(datetime.now().timestamp()))
        encoded = (sault + url + timestamp).encode("UTF-8")
        h = hashlib.md5(encoded).hexdigest()
        self.session.headers.update({"Timestamp": timestamp,
                                     "Hash": "v1:" + h,
                                     })

    def __get_prepared_url(self, url, **kwargs):
        p = requests.models.PreparedRequest()
        p.prepare(method="GET", url=url, **kwargs)
        return p.url

def pprint_json(json_str):
    try:
        json_object = json.loads(json_str)
        json_formatted_str = json.dumps(json_object, indent=2, ensure_ascii=False).encode('utf8')
        print(json_formatted_str.decode())
    except:
        pass
        print(json_str)

def get_guid_of_regione(regione) -> str:
    offers_url = 'https://geo-service.domclick.ru/research/api/v1/autocomplete/regions'
    dca = DomClickApi()
    res = dca.get(offers_url, params={
        "name": regione  #<<-- you regione str
    })
    count_obj = json.loads(res.text)
    print(count_obj['answer']['items'][0]['guid'])
    
    return count_obj['answer']['items'][0]['guid']

def main_parser_fn(addresse, database, user, password, host, port):    
    #main params
    offset = 0
    remont = ['standard', 'design', 'office_finishing', 'simple', 'required_cosmetic', 'required_repair', 'well_done', 'without_repair'] #without_repair design standard well_done
    balcons = [1, 2]
    rooms = [1, 2, 3, 4]
    type_dome = ['layout', 'flat'] 
    perec = ['brick', 'wood', 'monolith', 'panel', 'block', 'brick_monolith', 'shield', 'frame', 'foamed_block', 'gaz_block', 'metal']
    offers_url = 'https://offers-service.domclick.ru/research/v5/offers/'
    count_url = 'https://offers-service.domclick.ru/research/v5/offers/count/'

    dca = DomClickApi()
    for type in perec:
        for room in rooms:
            for sd in type_dome:
                for rem in remont:
                    for balcon in balcons:
                        req = dca.get(count_url, params={
                            "address": addresse,
                            "deal_type": "sale",
                            "category": "living",
                            "offer_type": [sd],
                            'renovation': rem,
                            'rooms': room,
                            "wall_type": type,
                            "balconies": balcon
                        })

                        count_obj = json.loads(req.text)
                        total = count_obj["pagination"]["total"]
                        
                        for offset in range(0, total, 1):
                            try: 
                                res = dca.get(offers_url, params={
                                            "address": addresse,
                                            "deal_type": "sale",
                                            "category": "living",
                                            "offer_type": [sd],
                                            "offset": offset,
                                            "limit": 10,
                                            'rooms': room,
                                            "wall_type": type,
                                            "renovation": rem,
                                            'balconies': balcon
                                })
                                #print("RES:", res)
                                offers_obj = json.loads(res.text)
                                result_data = offers_obj['result']
                                #print(res.text)
                                items = result_data['items']
                                #print(items)
                                for item in items:
                                    address = item['address']
                                    price = item['price_info']
                                    object_info = item['object_info']
                                    row = (address['name'],
                                           price['price'],
                                           price['square_price'],
                                           object_info['floor'],
                                           object_info['rooms'],
                                           object_info['area'],
                                           address['locality']['name'],
                                           sd,
                                           rem,
                                           balcon,
                                           address['guid'])
                                    
                                    tobd(row, database, user, password, host, port)                        
                            except ConnectionError:
                                print("error")
                                continue
    return 0                    
