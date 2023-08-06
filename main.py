import requests
import hashlib
from datetime import datetime


class DomClickApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-Service": "true",
                                     "Connection": "Keep-Alive",
                                     "User-Agent": "Android; 12; Google; sdk_gphone64_arm64; 8.72.0; 8720006; ; NONAUTH"
                                     })

        self.get("https://api.domclick.ru/core/no-auth-zone/api/v1/ensure_session")
        self.get("https://ipoteka.domclick.ru/mobile/v1/feature_toggles")

    def get(self, url, *args, **kwargs):
        self.update_headers(url)
        result = self.session.get(url, *args, **kwargs)
        return result

    def update_headers(self, url):
        sault = "ad65f331b02b90d868cbdd660d82aba0"
        timestamp = str(int(datetime.now().timestamp()))

        encoded = (sault + url + timestamp).encode("UTF-8")
        h = hashlib.md5(encoded).hexdigest()

        self.session.headers.update({"Timestamp": timestamp,
                                     "Hash": "v1:" + h,
                                     })


def pprint_json(json_str):
    import json
    json_object = json.loads(json_str)
    json_formatted_str = json.dumps(json_object, indent=2, ensure_ascii=False).encode('utf8')
    print(json_formatted_str.decode())


offers_url = 'https://offers-service.domclick.ru/research/v5/offers/?address=1d1463ae-c80f-4d19-9331-a1b68a85b553&aids=2299&category=living&deal_type=sale&ne=56.13937412952625%2C37.96779894140121&offer_type=flat&offer_type=layout&sale_price_full=1&sw=55.02108191587969%2C36.8032680585988&zoom=8&sort=qi&sort_dir=desc&offset=0&limit=20'

dca = DomClickApi()
res = dca.get(offers_url)
print("RES:", res)
pprint_json(res.text)
