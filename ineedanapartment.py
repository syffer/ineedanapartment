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
import alerts.freemobile
import retrievers.ouestfrance
import retrievers.aggregator
import criterias
import savers.redis
import savers.local


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

    if args.sms_free_mobile:
        (free_mobile_user, free_mobile_password) = args.sms_free_mobile
        free_mobile_alerter = alerts.freemobile.FreeMobileSelfSmsAlerter(free_mobile_user, free_mobile_password)
        alerter_manager.add_alerter(free_mobile_alerter)

    if args.sms_twilio:
        (username, from_number, to_number, password) = args.sms_twilio
        sms_alerter = alerts.sms.TwilioSmsAlerter(
            username=username,
            password=password,
            from_number=from_number,
            to_number=to_number
        )
        alerter_manager.add_alerter(sms_alerter)

    saver = savers.redis.RedisLocationSaver(args.redis_url) if args.redis_url else savers.local.LocalLocationsSaver()
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


def merge_env_variable(*env_vars, into=None):
    if not into:
        raise ValueError("'into' argument cannot be None")

    env_var_values = [os.environ.get(key) for key in env_vars]
    if not os.environ.get(into) and all(env_var_values):
        os.environ[into] = "[" + ", ".join(env_var_values) + "]"


if __name__ == "__main__":
    # fix: permettre de décomposer les variables d'environnement en plusieurs petites variables d'environnement
    merge_env_variable("EMAIL_HOST", "EMAIL_PORT", "EMAIL_USER", into="EMAIL")
    merge_env_variable("FREE_MOBILE_USER", into="SMS_FREE_MOBILE")
    merge_env_variable("TWILIO_USER", "TWILIO_NUMBER_FROM", "TWILIO_NUMBER_TO", into="SMS_TWILIO")

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
    # TODO change / add other savers depending on config
    parser.add_argument("--redis", dest="redis_url", env_var="REDIS_URL")

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
    alert_group.add_argument("--sms-free-mobile", nargs=1, metavar=("USER_LOGIN",), env_var="SMS_FREE_MOBILE",
                             action="append",
                             help="alerts via sms using a free mobile account. Will ask for the free mobile password")
    alert_group.add_argument("--sms-twilio", nargs=3, metavar=("USERNAME", "FROM_NUMBER", "TO_NUMBER"),
                             env_var="SMS_TWILIO",
                             help="alerts via an sms using a twilio account. Will ask for Twilio token")

    args = parser.parse_args()

    # getting the email password either in environment variable or via a prompt
    email_password = None if "--email" in sys.argv else os.environ.get("EMAIL_PASSWORD")
    if args.email and not email_password:
        email_password = getpass.getpass(prompt="Email password: ")

    if args.email:
        args.email.append(email_password)

    # getting the free mobile sms notification password
    free_mobile_password = None if "--sms-free-mobile" in sys.argv else os.environ.get("FREE_MOBILE_PASSWORD")
    if args.sms_free_mobile and not free_mobile_password:
        free_mobile_password = getpass.getpass(prompt="Free mobile sms notification password: ")

    if args.sms_free_mobile:
        args.sms_free_mobile.append(free_mobile_password)

    # getting the sms twilio token either in environment variable or via a prompt
    twilio_token = None if "--sms-twilio" in sys.argv else os.environ.get("TWILIO_TOKEN")
    if args.sms_twilio and not twilio_token:
        twilio_token = getpass.getpass(prompt="Token: ")

    if args.sms_twilio:
        args.sms.append(twilio_token)

    main(args)
