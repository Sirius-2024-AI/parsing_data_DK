import json
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
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

def get_data_a(dca, uri, addres):        
    res = dca.get(uri, params={
                                "address": addres,
                                "deal_type": "sale",
                                "category": "living",
                                "offer_type": ['flat'],
                                })
    return res

def get_data_b(dca, uri, addres, offset):        
    res = dca.get(uri, params={
                                "address": addres,
                                "deal_type": "sale",
                                "category": "living",
                                "offer_type": ['flat'],
                                "offset": offset
                                })
    return res

def get_extra_data_god(dca, ui):
    res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
    soup = BeautifulSoup(res.content, 'html.parser')
    s = soup.findAll('section', class_="EBeSC")
    for d in s:
        f = d.find('span', class_="ffG_w")
        return f.text

def get_extra_data_rem(dca, ui):
    res = dca.get(f"https://domclick.ru/card/sale__flat__{ui}", params={})
    soup = BeautifulSoup(res.content, 'html.parser')
    s = soup.findAll('section', class_="product-page__section")
    for d in s:
        f = d.find('span', class_="ffG_w")
        return f.text


def parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, dca):
    offset = 0

    req = get_data_a(DomClickApi(), count_url, addresse)
    #print(req.txt)                
    count_obj = json.loads(req.text)
    total = count_obj["pagination"]["total"]
            #print(count_obj['result'])
            #print(total)
    for offset in range(0, 1, 1):
        res = get_data_b(DomClickApi(), offers_url, addresse, offset)
                    
        offers_obj = json.loads(res.text)
        result_data = offers_obj["result"]
        items = result_data["items"]
        #print(res.text)
        for item in items:
            address = item['address']
            price = item['price_info']
            house = item['house']
            object_info = item['object_info']
            url = item['id']
            row = (
                   address['name'],
                   price['price'],
                   object_info['floor'],
                   house['floors'],
                   object_info['rooms'],
                   object_info['area'],
                   address['locality']['name'],
                   get_extra_data_god(DomClickApi(), url),
                   get_extra_data_rem(DomClickApi(), url),
                   )
                    #                )#print(row)
                    #    tobd(row, database, user, password, host, port, tablename)  
            print(row)                      

    return total
def main_parser_fn(addresse, database, user, password, host, port, tablename):#, database, user, password, host, port):    
    #main params
    offers_url = "https://offers-service.domclick.ru/research/v5/offers/"
    count_url = "https://offers-service.domclick.ru/research/v5/offers/count/"
    percents = parser(addresse, database, user, password, host, port, tablename, offers_url, count_url, DomClickApi())
    print('\rNAYDENO: {}'.format(percents), end='')
    return 0                    
