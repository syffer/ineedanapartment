# coding: utf-8

import argparse
import getpass
import time

import alerts.manager
import alerts.mails
import alerts.sms
import alerts.logs
import retrievers.ouestfrance
import retrievers.aggregator
import criterias


def main(args):
    alerter_manager = alerts.manager.AlerterManager()
    alerter_manager.add_alerter(alerts.logs.LogAlerter())

    if args.email:
        (host, port, user, password) = args.email
        email_alerter = alerts.mails.SelfEmailAlerter(
            host=host,
            port=port,
            user=user,
            password=password
        )
        alerter_manager.add_alerter(email_alerter)

    if args.sms:
        (username, from_number, to_number, password) = args.sms
        sms_alerter = alerts.sms.TwilioSmsAlerter(
            username=username,
            password=password,
            from_number=from_number,
            to_number=to_number
        )
        alerter_manager.add_alerter(sms_alerter)

    criteria = criterias.Criteria(**vars(args))
    retriever = retrievers.ouestfrance.OuestFranceLocationRetriever()
    aggregator = retrievers.aggregator.LocationAggregator(retriever)

    try:
        while True:
            new_locations = aggregator.retrieve_new_locations(criteria)
            if not new_locations:
                return

            alerter_manager.alert(new_locations)
            time.sleep(args.period)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Easy way to get notified when a new apartment appears on ouest france for nantes."
    )

    parser.add_argument("--period", nargs="?", const=5, default=5, type=int, help="delay between each check in seconds")

    criteria_group = parser.add_argument_group("Criteria")
    criteria_group.add_argument("--min-price", type=int)
    criteria_group.add_argument("--max-price", type=int)
    criteria_group.add_argument("--min-surface", type=int)
    criteria_group.add_argument("--max-surface", type=int)
    criteria_group.add_argument("--with-parking-spot", nargs="?", type=bool, const=True, default=False,
                                help="if the apartment must have a parking spot")

    alert_group = parser.add_argument_group("Alerts")
    alert_group.add_argument("--email", nargs=3, metavar=("HOST", "PORT", "EMAIL_FROM"),
                             help="alerts via an email. Will ask for the email password")
    alert_group.add_argument("--sms", nargs=3, metavar=("USERNAME", "FROM_NUMBER", "TO_NUMBER"),
                             help="alerts via an sms. Will ask for Twilio token")

    args = parser.parse_args()

    if args.email:
        email_password = getpass.getpass(prompt="Email password: ")
        args.email.append(email_password)

    if args.sms:
        token = getpass.getpass(prompt="Token: ")
        args.sms.append(token)

    main(args)
