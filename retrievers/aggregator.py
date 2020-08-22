# coding: utf-8

class LocationAggregator(object):
    __known_locations = set()

    def __init__(self, *retrievers):
        self.__retrievers = list(retrievers)

    def add_retriever(self, retriever):
        self.__retrievers.append(retriever)

    def retrieve_new_locations(self, criteria):
        retrieved_locations = self.__retrieve_locations(criteria)
        new_locations = retrieved_locations - self.__known_locations
        self.__known_locations.update(retrieved_locations)

        new_locations = list(new_locations)
        new_locations.sort(reverse=True)
        return new_locations

    def __retrieve_locations(self, criteria):
        return set(
            location
            for retriever in self.__retrievers
            for location in self.__safe_retrieve(retriever, criteria)
        )

    def __safe_retrieve(self, retriever, criteria):
        try:
            return retriever.retrieve(criteria)
        except Exception as e:
            print("=> cannot retrieve locations with {} because {}".format(type(retriever), e))
            return set()
