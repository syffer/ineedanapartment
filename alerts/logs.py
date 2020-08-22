# coding: utf-8

import alerts.alerter


class LogAlerter(alerts.alerter.Alerter):

    def alert(self, locations):
        print("New locations:")
        for location in locations:
            print("- {location.website} {location} {location.link}".format(location=location))
        print("")
