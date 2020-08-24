# coding: utf-8

import requests

import alerts.alerter


class FreeMobileSelfSmsAlerter(alerts.alerter.Alerter):

    def __init__(self, user_login, password):
        self.user_login = user_login
        self.password = password

    def alert(self, locations):
        message = "{location.website} {location} {location.link}".format(location=locations[0])

        url = "https://smsapi.free-mobile.fr/sendmsg"
        params = {
            "user": self.user_login,
            "pass": self.password,
            "msg": message,
        }
        requests.get(url, params=params)
