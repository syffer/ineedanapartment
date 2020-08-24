# coding: utf-8

import jsonpickle


class LocationsSaver(object):
    FILE_PATH = "saved_locations.json"

    def __init__(self):
        pass

    def load_locations(self):
        try:
            with open(self.FILE_PATH, "r") as file:
                content = file.read()
                return jsonpickle.decode(content)
        except Exception:
            return set()

    def save_locations(self, locations):
        with open(self.FILE_PATH, "w") as file:
            content = jsonpickle.encode(locations)
            file.write(content)
