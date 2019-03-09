from configparser import ConfigParser
import datetime
import json
import random
from time import sleep
from uuid import uuid4

import boto3
from pytz import timezone

DEFAULT_SETTINGS = {
    "events_per_sec": 10,
    "sqs_name": "SomeSQS",
}
EVENT_TYPES = ["submission_success", "registration_initiated", "another_event"]
EVENT_TYPE_TEXT = {
    "submission_success": "submissionSuccess",
    "registration_initiated": "registrationInitiated",
    "another_event": "anotherEvent",
}
PLATFORMS = ["android", "ios"]
OS_NAME = {
    "android": "Android",
    "ios": "iOS",
}
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
BERLIN_TZ = timezone("Europe/Berlin")


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "events_per_sec": config.getint("events", "events_per_sec", fallback=DEFAULT_SETTINGS["events_per_sec"]),
        "sqs_name": config.get("aws", "sqs_name", fallback=DEFAULT_SETTINGS["sqs_name"]),
    }


def generate_sample_event() -> dict:
    """
    Generates a semi-random event

    :return: a single event dictionary
    """
    # Assumed order of timestamps: original -> timestamp -> sent -> received
    # Generation is moving from the latest (received) backwards in time with random shifts
    received_at = datetime.datetime.utcnow()
    sent_at = received_at - datetime.timedelta(microseconds=random.randint(100, 2000))
    ts = sent_at - datetime.timedelta(microseconds=random.randint(100, 1000))
    original_ts = ts - datetime.timedelta(microseconds=random.randint(0, 100))
    # Select random event type and platform
    event_type = random.choice(EVENT_TYPES)
    platform = random.choice(PLATFORMS)
    # Rest of the fields are not important for the task context, so left hardcoded
    event = {
        "id": str(uuid4()).upper(),
        "received_at": received_at.strftime(DATETIME_FORMAT),
        "anonymous_id": str(uuid4()).upper(),
        "context_device_manufacturer": "Apple",
        "context_device_model": "iPhone8,4",
        "context_device_type": platform,
        "context_locale": "de-DE",
        "context_network_wifi": random.choice([False, True]),
        "context_os_name": OS_NAME[platform],
        "event": event_type,
        "event_text": EVENT_TYPE_TEXT[event_type],
        "original_timestamp": original_ts.astimezone(BERLIN_TZ).strftime(f"{DATETIME_FORMAT}%z"),
        "sent_at": sent_at.strftime(DATETIME_FORMAT),
        "timestamp": ts.strftime(DATETIME_FORMAT),
        "context_network_carrier": "o2-de",
        "context_traits_taxfix_language": "en-DE",
    }

    optional_fields = {
        "context_app_version": "1.2.3",
        "context_device_ad_tracking_enabled": random.choice([False, True]),
        "context_library_name": "analytics-ios",
        "context_library_version": "3.6.7",
        "context_timezone": "Europe/Berlin",
        "user_id": str(random.randint(1, 10000000)),
        "context_device_token": None,
    }
    addition = random.choices(list(optional_fields.keys()), k=random.randint(0, len(optional_fields)))
    event.update({
        key: optional_fields[key] for key in addition
    })

    return event


if __name__ == "__main__":
    settings = load_settings()

    # Settings contains an approximate amount of events per second we want to have
    # which gives an average interval between messages of 1s / events_per_sec
    # In order to have an average interval appearing more often we will use
    # [0, 2 * avg_interval) as random boundaries
    interval = 2 * 1.0 / settings["events_per_sec"]

    # Connect to SQS
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=settings["sqs_name"])

    # Start an endless loop of message sending
    while True:
        # Send an event to the queue
        event = generate_sample_event()
        response = queue.send_message(MessageBody=json.dumps(event))
        print(response.get('MessageId'))

        # Sleep until the next event
        sleep(random.random() * interval)
