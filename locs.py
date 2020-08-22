# coding: utf-8

import functools


@functools.total_ordering
class Location(object):
    def __init__(self, _id, title, link, date, price, surface, others=None, website=None):
        self.id = _id
        self.title = title
        self.link = link
        self.price = price
        self.surface = surface
        self.others = others
        self.date = date
        self.website = website

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ge__(self, other):
        return (self.date, other.price, self.surface, self.title) > (other.date, self.price, other.surface, other.title)

    def __repr__(self):
        formatted_date = self.date
        return "{}€ {} {} {}".format(self.price, self.surface, self.title, formatted_date, self.others)
