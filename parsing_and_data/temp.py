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
count_url = 'https://geo-service.domclick.ru/research/api/v1/autocomplete/regions'

dca = DomClickApi()
res = dca.get(count_url, params={
    "name": "Москва"
})
print("RES:", res)
print(res.text)
pprint_json(res.text)

