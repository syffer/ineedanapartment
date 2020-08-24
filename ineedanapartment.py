# coding: utf-8

import argparse
import getpass
import os
import time

import alerts.manager
import alerts.mails
import alerts.sms
import alerts.logs
import retrievers.ouestfrance
import retrievers.aggregator
import criterias
import savers


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

    saver = savers.LocationsSaver()
    known_locations = saver.load_locations() if args.save_locations else set()

    criteria = criterias.Criteria(**vars(args))
    retriever = retrievers.ouestfrance.OuestFranceLocationRetriever()
    aggregator = retrievers.aggregator.LocationAggregator(retriever, known_locations=known_locations)

    try:
        while True:
            new_locations = aggregator.retrieve_new_locations(criteria, args.since)
            if new_locations:
                alerter_manager.alert(new_locations)

            if args.save_locations:
                saver.save_locations(aggregator.get_known_locations())

            time.sleep(args.period)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Easy way to get notified when a new apartment appears on ouest france for nantes."
    )

    parser.add_argument("--period", nargs="?", const=5, default=5, type=int, help="delay between each check in seconds")
    parser.add_argument("--since", nargs="?", type=int, default=3, choices=range(1, 30))
    parser.add_argument("--save-locations", nargs="?", type=bool, const=True, default=False,
                        help="Save locations between executions")

    criteria_group = parser.add_argument_group("Criteria")
    criteria_group.add_argument("--min-price", type=int)
    criteria_group.add_argument("--max-price", type=int)
    criteria_group.add_argument("--min-surface", type=int)
    criteria_group.add_argument("--max-surface", type=int)
    criteria_group.add_argument("--with-parking-spot", nargs="?", type=bool, const=True, default=False,
                                help="if the apartment must have a parking spot")

    alert_group = parser.add_argument_group("Alerts")

    default_email = (
        os.environ.get("EMAIL_HOST"),
        os.environ.get("EMAIL_PORT"),
        os.environ.get("EMAIL_FROM")
    )
    default_email = default_email if all(default_email) else None
    alert_group.add_argument("--email", nargs=3, metavar=("HOST", "PORT", "EMAIL_FROM"),
                             default=default_email,
                             help="alerts via an email. Will ask for the email password")

    default_sms = (
        os.environ.get("TWILIO_USERNAME"),
        os.environ.get("TWILIO_FROM_NUMBER"),
        os.environ.get("TWILIO_TO_NUMBER")
    )
    default_sms = default_sms if all(default_sms) else None
    alert_group.add_argument("--sms", nargs=3, metavar=("USERNAME", "FROM_NUMBER", "TO_NUMBER"),
                             default=default_sms,
                             help="alerts via an sms. Will ask for Twilio token")

    args = parser.parse_args()

    # getting the email password either in environment variable or via a prompt
    if args.email and args.email == default_email:
        email_password = os.environ.get("EMAIL_PASSWORD")
        args.email = list(args.email)
        args.email.append(email_password)

    elif args.email and args.email != default_email:
        email_password = getpass.getpass(prompt="Email password: ")
        args.email.append(email_password)

    # getting the sms twilio token either in environment variable or via a prompt
    if args.sms and args.sms == default_sms:
        twilio_token = os.environ.get("TWILIO_TOKEN")
        args.sms = list(args.sms)
        args.sms.append(twilio_token)

    elif args.sms:
        twilio_token = getpass.getpass(prompt="Token: ")
        args.sms.append(twilio_token)

    main(args)
