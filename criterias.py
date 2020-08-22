# coding: utf-8

class Criteria(object):

    def __init__(self,
                 min_price=None,
                 max_price=None,
                 min_surface=None,
                 max_surface=None,
                 with_parking_spot=False,
                 **kwargs):
        self.min_price = min_price
        self.max_price = max_price
        self.min_surface = min_surface
        self.max_surface = max_surface
        self.with_parking_spot = with_parking_spot
