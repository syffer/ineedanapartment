# coding: utf-8

import requests

import alerts.alerter


class FreeMobileSelfSmsAlerter(alerts.alerter.Alerter):

    FREE_MOBILE_URL_SEND_SMS = "https://smsapi.free-mobile.fr/sendmsg"

    def __init__(self, user_login, password):
        self.user_login = user_login
        self.password = password

    def alert(self, locations):
        for location in locations:
            message = "{location.website} {location} {location.link}".format(location=location)

            params = {
                "user": self.user_login,
                "pass": self.password,
                "msg": message,
            }
            response = requests.get(self.FREE_MOBILE_URL_SEND_SMS, params=params)
            response.raise_for_status()
