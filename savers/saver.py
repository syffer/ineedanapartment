# coding: utf-8

class LocationSaver(object):

    def load_locations(self):
        raise NotImplementedError("subclasses must override this method")

    def save_locations(self, locations):
        raise NotImplementedError("subclasses must override this method")
