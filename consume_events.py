from configparser import ConfigParser
from datetime import datetime
from io import BytesIO
import json
import logging
from uuid import uuid4

import boto3

DEFAULT_SETTINGS = {
    "sqs_name": "SomeSQS",
    "sqs_polling_timeout": 20,
    "s3_bucket": "SomeBucket",
}

CLIENTS = {
    "s3": boto3.client('s3'),
    "sqs": boto3.resource('sqs'),
}


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "sqs_name": config.get("aws", "sqs_name", fallback=DEFAULT_SETTINGS["sqs_name"]),
        "sqs_polling_timeout": config.getint("aws", "sqs_polling_timeout",
                                             fallback=DEFAULT_SETTINGS["sqs_polling_timeout"]),
        "s3_bucket": config.get("aws", "s3_bucket", fallback=DEFAULT_SETTINGS["s3_bucket"]),
    }


def save_to_dfs(events: list, bucket_name: str):
    """
    Saves a list of events to S3 bucket
    :param events: list of raw events
    :param bucket_name: name of S3 bucket
    :return: None
    """
    if not events:
        return

    s = BytesIO(bytes(json.dumps(events), 'utf-8'))
    today = datetime.utcnow().strftime("%Y%m%d/%H%M%S")
    CLIENTS["s3"].upload_fileobj(s, bucket_name, f"{today}-{uuid4()}.json")
    s.close()


def fetch_events(settings: dict):
    """
    Ingest events from SQS and save them to a DFS

    :param settings: settings dictionary
    :return: None
    """
    queue = CLIENTS["sqs"].get_queue_by_name(QueueName=settings["sqs_name"])
    events = []

    while True:
        to_delete = []
        for message in queue.receive_messages(MaxNumberOfMessages=10,
                                              WaitTimeSeconds=settings["sqs_polling_timeout"]):
            try:
                events.append(json.loads(message.body))
            except json.JSONDecodeError:
                logging.error("Could not decode an event ", message.body)
                continue

            to_delete.append({"Id": message.message_id, "ReceiptHandle": message.receipt_handle})

        if to_delete:
            queue.delete_messages(Entries=to_delete)

        # TODO: do not save every time, collect some batch
        save_to_dfs(events, settings["s3_bucket"])
        events = []


if __name__ == "__main__":
    settings = load_settings()

    # Start a loop of events fetching
    fetch_events(settings)
