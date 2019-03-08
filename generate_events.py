from configparser import ConfigParser
import datetime
import json
import random
from time import sleep
from uuid import uuid4

DEFAULT_SETTINGS = {
    "events_per_sec": 10,
    "foo": "bar"
}
EVENT_TYPES = ["submission_success", "registration_initiated", "another_event"]
EVENT_TYPE_TEXT = {
    "submission_success": "submissionSuccess",
    "registration_initiated": "registrationInitiated",
    "another_event": "anotherEvent"
}
PLATFORMS = ["android", "ios"]


def load_settings() -> dict:
    config = ConfigParser()
    config.read("settings.ini")
    if "events" not in config:
        return DEFAULT_SETTINGS

    section = config["events"]
    return {
        key: section.get(key, DEFAULT_SETTINGS[key])
        for key in DEFAULT_SETTINGS.keys()
    }


def generate_sample_event() -> dict:
    now = datetime.datetime.utcnow()
    event_type = random.choice(EVENT_TYPES)
    platform = random.choice(PLATFORMS)
    event = {
        "id": str(uuid4()).upper(),
        "received_at": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "anonymous_id": str(uuid4()).upper(),
        "context_device_manufacturer": "Apple",
        "context_device_model": "iPhone8,4",
        "context_device_type": platform,
        "context_locale": "de-DE",
        "context_network_wifi": random.choice([False, True]),
        "context_os_name": "android",
        "event": event_type,
        "event_text": EVENT_TYPE_TEXT[event_type],
        # TODO: base on `now` value
        "original_timestamp": "2018-01-30T19:13:43.383+0100",
        "sent_at": "2018-01-30 18:13:51.000000",
        "timestamp": "2018-01-30 18:13:43.627000",
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
    while True:
        print(json.dumps(generate_sample_event(), indent=4))
        # TODO: add randomization in the delay based on settings
        sleep(1)
