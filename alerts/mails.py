# coding: utf-8

import smtplib
import email.mime.text
import email.mime.multipart

import alerts.alerter


class SelfEmailAlerter(alerts.alerter.Alerter):

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def alert(self, locations):
        mail = email.mime.multipart.MIMEMultipart()
        mail["Subject"] = "Nouvelles locations"

        text = ""
        for location in locations:
            text += """{location.website} <a href="{location.link}">{location}</a><br><br>""".format(location=location)

        content = email.mime.text.MIMEText(text, "html")
        mail.attach(content)

        send_mail(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            mail=mail
        )


# smtplib.SMTPAuthenticationError: (535, b'5.7.3 Authentication unsuccessful [PR0P264CA0262.FRAP264.PROD.OUTLOOK.COM]')

def send_mail(host, port, user, password, mail, to_addr=None):
    # set up the SMTP server
    with smtplib.SMTP(host=host, port=port) as smtp:
        smtp.starttls()
        smtp.login(user, password)

        if not to_addr:
            to_addr = user

        # mail = email.mime.multipart.MIMEMultipart()
        mail["From"] = user
        mail["To"] = to_addr
        smtp.send_message(mail, to_addrs=[to_addr])
