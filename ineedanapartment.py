# coding: utf-8

import argparse
import configargparse
import getpass
import os
import sys
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
    # fix: permettre de décomposer les variables d'environnement EMAIL et SMS_TWILIO en plusieurs petites variables d'environnement
    email_info = [os.environ.get(key) for key in ("EMAIL_HOST", "EMAIL_PORT", "EMAIL_FROM")]
    if not os.environ.get("EMAIL") and all(email_info):
        os.environ["EMAIL"] = "[" + ", ".join(email_info) + "]"

    sms_twilio_info = [os.environ.get(key) for key in ["TWILIO_USER", "TWILIO_NUMBER_FROM", "TWILIO_NUMBER_TO"]]
    if not os.environ.get("SMS_TWILIO") and all(sms_twilio_info):
        os.environ["SMS_TWILIO"] = "[" + ", ".join(sms_twilio_info) + "]"

    #
    parser = configargparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Easy way to get notified when a new apartment appears on ouest france for nantes."
    )

    parser.add_argument("--period", nargs="?", default=5 * 60, type=int, env_var="PERIOD",
                        help="delay between each check in seconds")
    parser.add_argument("--since", nargs="?", type=int, default=3, choices=range(1, 30), env_var="SINCE")
    parser.add_argument("--save-locations", nargs="?", type=bool, const=True, default=False, env_var="SAVE_LOCATIONS",
                        help="Save locations between executions")

    criteria_group = parser.add_argument_group("Criteria")
    criteria_group.add_argument("--min-price", type=int, env_var="MIN_PRICE")
    criteria_group.add_argument("--max-price", type=int, env_var="MAX_PRICE")
    criteria_group.add_argument("--min-surface", type=int, env_var="MIN_SURFACE")
    criteria_group.add_argument("--max-surface", type=int, env_var="MAX_SURFACE")
    criteria_group.add_argument("--with-parking-spot", nargs="?", type=bool, const=True, default=False,
                                env_var="WITH_PARKING_SPOT",
                                help="if the apartment must have a parking spot")

    alert_group = parser.add_argument_group("Alerts")
    alert_group.add_argument("--email", nargs=3, metavar=("HOST", "PORT", "EMAIL_FROM"), env_var="EMAIL",
                             help="alerts via an email. Will ask for the email password")
    alert_group.add_argument("--sms", nargs=3, metavar=("USERNAME", "FROM_NUMBER", "TO_NUMBER"), env_var="SMS_TWILIO",
                             help="alerts via an sms. Will ask for Twilio token")

    args = parser.parse_args()

    # getting the email password either in environment variable or via a prompt
    email_password = None if "--email" in sys.argv else os.environ.get("EMAIL_PASSWORD")
    if args.email and not email_password:
        email_password = getpass.getpass(prompt="Email password: ")

    if args.email:
        args.email.append(email_password)

    # getting the sms twilio token either in environment variable or via a prompt
    twilio_token = None if "--sms" in sys.argv else os.environ.get("TWILIO_TOKEN")
    if args.sms and not twilio_token:
        twilio_token = getpass.getpass(prompt="Token: ")

    if args.sms:
        args.sms.append(twilio_token)

    main(args)
