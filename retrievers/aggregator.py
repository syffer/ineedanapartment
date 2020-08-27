# coding: utf-8

import datetime
import traceback


class LocationAggregator(object):
    __known_locations = set()

    def __init__(self, *retrievers, known_locations=None):
        self.__retrievers = list(retrievers)
        self.__known_locations = set(known_locations) if known_locations else set()

    def add_retriever(self, retriever):
        self.__retrievers.append(retriever)

    def retrieve_new_locations(self, criteria, since=1):
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - datetime.timedelta(days=since)

        retrieved_locations = self.__retrieve_locations(criteria, yesterday)
        new_locations = retrieved_locations - self.__known_locations
        self.__known_locations = {location for location in self.__known_locations if location.date > yesterday}
        # unknown_locations = self.__known_locations - retrieved_locations
        # self.__known_locations.difference_update(unknown_locations)
        self.__known_locations.update(retrieved_locations)

        new_locations = list(new_locations)
        new_locations.sort(reverse=True)
        return new_locations

    def __retrieve_locations(self, criteria, from_date):
        return set(
            location
            for retriever in self.__retrievers
            for location in self.__safe_retrieve(retriever, criteria)
            if location.date > from_date
        )

    def __safe_retrieve(self, retriever, criteria):
        try:
            return retriever.retrieve(criteria)
        except Exception as e:
            print("=> cannot retrieve locations with {} because {}".format(type(retriever), e))
            traceback.print_exc()
            return set()

    def get_known_locations(self):
        return self.__known_locations
