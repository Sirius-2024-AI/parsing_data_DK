import json
import time
import requests
import hashlib
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
        self.__update_headers(url, **kwargs)
        result = self.session.get(url, **kwargs)
        print(self.session.cookies.get_dict())
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
        print(json_str)


offers_url = 'https://offers-service.domclick.ru/research/v5/offers/'
count_url = 'https://offers-service.domclick.ru/research/v5/offers/count/'

dca = DomClickApi()
res = dca.get(count_url, params={
    "address": "26f533ee-f4c6-4fd8-9cb5-a1910250622e",
    "deal_type": "sale",
    "category": "living",
    "offer_type": ["flat", "layout"],
    "rooms": ["1", "2"],
    "area__gte": 50,
    "floor__gte": 7,
})
print("RES:", res)
print(res.text)
pprint_json(res.text)

count_obj = json.loads(res.text)
total = count_obj["pagination"]["total"]

offset = 0
while offset < total:
    res = dca.get(offers_url, params={
        "address": "26f533ee-f4c6-4fd8-9cb5-a1910250622e",
        "deal_type": "sale",
        "category": "living",
        "offer_type": ["flat", "layout"],
        "rooms": ["1", "2"],
        "area__gte": 50,
        "floor__gte": 7,

        "sort": "qi",
        "sort_dir": "desc",
        "offset": offset,
        "limit": 30,
    })
    print("RES:", res)
    pprint_json(res.text)
    offset += 30
    offers_obj = json.loads(res.text)
    total = offers_obj["pagination"]["total"]
    print(f"{offset}/{total}")
