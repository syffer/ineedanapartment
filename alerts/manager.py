# coding: utf-8

class AlerterManager(object):

    def __init__(self, *args):
        self.__alerters = list(args)

    def alert(self, locations):
        for alerter in self.__alerters:
            try:
                alerter.alert(locations)
            except Exception as e:
                print("=> cannot alert using {} because {}".format(type(alerter), e))

    def add_alerter(self, alerter):
        self.__alerters.append(alerter)
