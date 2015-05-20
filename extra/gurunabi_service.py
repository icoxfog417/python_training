import os
import json
from enum import Enum
import re
import asyncio
import urllib.request as request
import urllib.parse as parse
import webbrowser


class GurunabiApi(Enum):
    search = "/ver1/RestSearchAPI/"
    search_multilingual = "/ver2/RestSearchAPI/"
    prefectures = "/ver2/PrefSearchAPI/"
    cheers = "/ouen/ver1/PhotoSearch/"


class GurunabiService():
    """
    Provides interface to access Gurunabi API
    http://api.gnavi.co.jp/api/manual/
    """

    API_ROOT = "http://api.gnavi.co.jp"

    def __init__(self):
        """
        this initialization process will cause exception.
        It reads keyid from `api_key.json` file that is expected to locate in the same directory.
        :return:
        """

        self.keyid = ""

        my_dir = os.path.dirname(__file__)
        api_key_path = os.path.join(my_dir, "api_key.json")
        with open(api_key_path) as api_key_file:
            api_key = json.load(api_key_file)
            self.keyid = api_key["keyid"]

    def __search(self, api_type, key_words, optional, page_size, offset):
        required = {
            "keyid": self.keyid,
            "hit_per_page": page_size,
            "offset_page": offset,
            "freeword": ",".join(key_words),
            "format": "json"
        }
        params = self.__concat(required, optional)

        query = parse.urlencode(params)
        url = self.API_ROOT + api_type.value + "?" + query

        restaurants = []
        with request.urlopen(url) as resp:
            content = resp.read()
            result = json.loads(content.decode("utf-8"))
            if "rest" in result:
                if isinstance(result["rest"], dict):
                    restaurants = [Restaurant(result["rest"])]
                else:
                    restaurants = [Restaurant(r) for r in result["rest"]]

        return restaurants

    def search(self, key_words, prefecture=-1, page_size=10, offset=1):
        restaurants = []

        _key_words = key_words
        if isinstance(key_words, str):
            _key_words = [key_words]

        lang = self.judge_language(_key_words)
        optional = {}
        optional = self.__concat(optional, self.make_prefecture_filter(prefecture))
        if lang:
            optional = self.__concat(optional, {"lang": lang})
            restaurants = self.__search(GurunabiApi.search_multilingual, _key_words, optional, page_size, offset)
        else:
            restaurants = self.__search(GurunabiApi.search, _key_words, optional, page_size, offset)

        if len(restaurants) > 0:
            sem = asyncio.Semaphore(3)

            @asyncio.coroutine
            def set_cheers_async(restaurant):
                @asyncio.coroutine
                def __set_cheers(r):
                    self.set_cheers(r)

                with (yield from sem):
                    yield from __set_cheers(restaurant)

            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait([set_cheers_async(r) for r in restaurants]))

        return restaurants

    def set_cheers(self, restaurant):
        params = {
            "keyid": self.keyid,
            "shop_id": restaurant.id,
            "hit_per_page": restaurant.CHEERS_LIMIT,
            "offset_page": 1,
            "format": "json"
        }

        query = parse.urlencode(params)
        url = self.API_ROOT + GurunabiApi.cheers.value + "?" + query

        cheers = []
        with request.urlopen(url) as resp:
            content = resp.read()
            result = json.loads(content.decode("utf-8"))
            if "response" in result:
                for k in result["response"]:
                    if k.isdigit():
                        cheers.append(Cheer(result["response"][k]))

        restaurant.cheers = cheers

    @classmethod
    def make_prefecture_filter(cls, prefecture):
        if prefecture < 0:
            return {}
        else:
            code = "PREF" + str(prefecture).zfill(2)
            return {"pref": code}

    @classmethod
    def judge_language(cls, key_words):
        english_pattern = re.compile("^\w+$", re.ASCII)

        if cls.__is_match_pattern(key_words, english_pattern):
            return "en"
        else:
            return ""

    @classmethod
    def __is_match_pattern(cls, key_words, pattern):

        occurance = sum([pattern.match(w.replace(" ", "")) is not None for w in key_words])
        if occurance == len(key_words):
            return True
        else:
            return False

    def __concat(self, left, right):
        opt = lambda x: x if x is not None else {}

        result = opt(left)
        for k in opt(right):
            result[k] = opt(right)[k]

        return result


class Restaurant():
    CHEERS_LIMIT = 3

    def __init__(self, restaurant_json):
        _get = lambda d, k: "" if k not in d else d[k]

        self.id = _get(restaurant_json, "id")
        self.address = _get(restaurant_json, "address")
        self.url = _get(restaurant_json, "url")
        self.images = []
        if "image_url" in restaurant_json:
            self.images.append(_get(restaurant_json["image_url"], "shop_image1"))

        self.cheers = []

        self.name = ""
        self.name_kana = ""
        self.name_sub = ""

        if isinstance(restaurant_json["name"], str):
            self.name = restaurant_json["name"]
            self.name_kana = restaurant_json["name_kana"]
        else:
            names = restaurant_json["name"]
            self.name = names["name"]
            if "name_sub" in names:
                self.name_sub = names["name_sub"]
            else:
                self.name_kana = names["name_kana"]

    def __str__(self):
        sub_text = self.name_kana
        if not sub_text:
            sub_text = self.name_sub

        return "{0}({1})".format(self.name, sub_text)

    @classmethod
    def show_restaurants_page(cls, restaurants):
        page_template = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container">{0}</div>
        </body>
        </html>"""

        item_template = """
        <div class="row">
            <h3><a href="{0}" target="_blank">{1}</a></h3>
            <div class="col-md-4">
                <img src="{2}" alt="shop_image" class="img-thumbnail" style="max-height: 200px;"/>
            </div>
            <div class="col-md-8">
                {3}
                <br style='clear:both'/>
            </div>
        </div>
        """

        cheer_image = """
        <div style="float:left"><img src="{0}" style="max-height: 100px; margin-left:10px"/></div>
        """

        item_descriptions = []
        for r in restaurants:
            cheers = [cheer_image.format(c.images[-1]) for c in r.cheers]
            desc = item_template.format(r.url, r.name, "" if len(r.images) == 0 else r.images[0], "".join(cheers))
            item_descriptions.append(desc)

        html = page_template.format("".join(item_descriptions))
        with open("restaurants.html", "w", encoding="utf-8") as page:
            page.write(html)
        webbrowser.open_new_tab("restaurants.html")


class Cheer():

    def __init__(self, cheer_json):
        _get = lambda d, k: "" if k not in d else d[k]

        photo = cheer_json["photo"]

        self.id = _get(photo, "vote_id")
        self.menu_id = _get(photo, "menu_id")
        self.menu_name = _get(photo, "menu_name")
        self.menu_finish_flag = True if _get(photo, "menu_finish_flag") == 0 else False
        self.images = []
        if "image_url" in photo:
            for im in photo["image_url"].values():
                self.images.append(im)
