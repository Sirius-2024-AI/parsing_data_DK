import json
import requests
import hashlib
import pandas as pd
import traceback
from datetime import datetime

# these variables indicate by which values to filter the data
percents: int = 0
REPAIR: list = ["standard", "design", "office_finishing", "simple", "required_cosmetic", "required_repair", "well_done",
                "without_repair"]
BALCONY: list = [1, 2]
ROOMS: list = ["1", "st", "2", "3", "4"]
OFFER_TYPE: list = ['flat']
VIEW_FROM_WINDOW: list = ['garden', 'park', 'water', 'forest', 'street']
WALL_TYPE: list = ["brick", "wood", "monolith", "panel", "block", "brick_monolith", "shield", "frame", "foamed_block",
                   "gaz_block", "metal"]
OFFERS_URL: str = "https://offers-service.domclick.ru/research/v5/offers/"
COUNT_URL: str = "https://offers-service.domclick.ru/research/v5/offers/count/"


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
            return result
        except (ConnectionError, ConnectionResetError) as e:
            print(e)

    def __update_headers(self, url, **kwargs):
        url = self.__get_prepared_url(url, **kwargs)
        UNIC_KEY: str = "ad65f331b02b90d868cbdd660d82aba0"
        timestamp = str(int(datetime.now().timestamp()))
        encoded = (UNIC_KEY + url + timestamp).encode("UTF-8")
        h = hashlib.md5(encoded).hexdigest()
        self.session.headers.update({"Timestamp": timestamp,
                                     "Hash": "v1:" + h, })

    def __get_prepared_url(self, url, **kwargs):
        p = requests.models.PreparedRequest()
        p.prepare(method="GET", url=url, **kwargs)
        return p.url


def get_guid_region(region) -> str:  # this function receives the name of the region and returns its GUID
    GEO_URL = 'https://geo-service.domclick.ru/research/api/v1/autocomplete/regions'
    dca = DomClickApi()
    res = dca.get(GEO_URL, params={"name": region})
    count_obj = json.loads(res.text)
    GUID = count_obj['answer']['items'][0]['guid']
    print(f"{region} region found, guid: " + GUID)
    return GUID


def get_total_offers(dca, guid, view_from_window, repair, room, wall_type, balcony) -> int:
    req = dca.get(COUNT_URL, params={
        "address": guid,
        "deal_type": "sale",
        "category": "living",
        "window_view": view_from_window,
        "offer_type": OFFER_TYPE,
        "renovation": repair,
        "rooms": room,
        "wall_type": wall_type,
        "balconies": balcony
    })

    count_obj = json.loads(req.text)
    total = count_obj["pagination"]["total"]
    return total


def get_items(dca, guid, view_from_window, repair, room, wall_type, balcony, offset) -> list:
    res = dca.get(OFFERS_URL, params={
        "address": guid,
        "deal_type": "sale",
        "category": "living",
        "offer_type": OFFER_TYPE,
        "window_view": view_from_window,
        "offset": offset,
        "limit": 1,
        "rooms": room,
        "wall_type": wall_type,
        "renovation": repair,
        "balconies": balcony,
    })

    offers_obj = json.loads(res.text)
    result_data = offers_obj["result"]
    items = result_data["items"]
    return items


def parser(guid, view_from_window, repair, room, balcony, wall_type, file):
    offset = 0
    dataset = []
    dca = DomClickApi()
    try:
        total = get_total_offers(dca, guid, view_from_window, repair, room, wall_type, balcony)
        for offset in range(0, total, 1):
            items = get_items(dca, guid, view_from_window,
                              repair, room, wall_type, balcony, offset)
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
                    "total_floors": house['floors'],
                    "rooms": object_info['rooms'],
                    "area": object_info['area'],
                    "region": address['locality']['name'],
                    "repair": repair,
                    "balcony": balcony,
                    "url": url,
                    "view_from_window": view_from_window,
                    "wall_type": wall_type,

                }
                dataset.append(row)

        df = pd.DataFrame(dataset)
        df.to_csv(file, mode='a', header=False)
    except Exception:
        print(traceback.format_exc())


def main_parser_fn(address, file):
    for room in ROOMS:
        for view_from_window in VIEW_FROM_WINDOW:
            for wall_type in WALL_TYPE:
                for balcony in BALCONY:
                    for repair in REPAIR:
                        parser(address, view_from_window, repair, room, balcony, wall_type, file)
    return 0
