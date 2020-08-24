# coding: utf-8

import jsonpickle
import redis

import savers.saver


class RedisLocationSaver(savers.saver.LocationSaver):
    LOCATIONS_KEY = "locations"

    def __init__(self, url):
        self.__url = url

    def load_locations(self):
        try:
            with self.__get_redis() as r:
                encoded_content = r.get(self.LOCATIONS_KEY)
                return jsonpickle.decode(encoded_content)
        except Exception:
            return set()

    def save_locations(self, locations):
        content = jsonpickle.encode(locations)

        with self.__get_redis() as r:
            r = self.__get_redis()
            r.set(self.LOCATIONS_KEY, content)

    def __get_redis(self):
        return redis.from_url(self.__url)
