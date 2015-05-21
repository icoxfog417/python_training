import os
import json
from enum import Enum
import re
import asyncio
import urllib.request as request
import urllib.parse as parse
from extra.models import Restaurant, Cheer


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
        """
        call search api
        :param api_type: GurunabiApi.search or GurunabiApi.search_multilingual
        :param key_words:
        :param optional: optional request parameters
        :param page_size:
        :param offset:
        :return:
        """

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
        """
        public interface to call search api
        :param key_words:
        :param prefecture:
        :param page_size:
        :param offset:
        :return:
        """
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
            self.set_cheers(restaurants)

        return restaurants

    def set_cheers(self, restaurants):
        # set cheers to restaurant by parallel
        sem = asyncio.Semaphore(3)  # limit the parallel process

        @asyncio.coroutine
        def set_cheers_async(restaurant):
            @asyncio.coroutine
            def __set_cheers(r):
                self._set_cheers(r)

            with (yield from sem):
                yield from __set_cheers(restaurant)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait([set_cheers_async(r) for r in restaurants]))

    def _set_cheers(self, restaurant):
        """
        set cheers to restaurant
        :param restaurant:
        :return:
        """
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
        if len(key_words) == 0:
            return False

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

