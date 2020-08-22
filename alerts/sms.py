# coding: utf-8

import twilio.rest

import alerts.alerter


# another option https://dashboard.sinch.com/signup

class TwilioSmsAlerter(alerts.alerter.Alerter):

    def __init__(self, username, password, from_number, to_number):
        self.username = username
        self.password = password
        self.from_number = from_number
        self.to_number = to_number

    def alert(self, locations):
        message = "{location.website} {location} {location.link}".format(location=locations[0])

        send_sms(
            username=self.username,
            password=self.password,
            from_number=self.from_number,
            to_number=self.to_number,
            message=message
        )


def send_sms(username, password, from_number, to_number, message):
    client = twilio.rest.Client(username=username, password=password)
    client.messages.create(from_=from_number, to=to_number, body=message)
