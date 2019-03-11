from configparser import ConfigParser
from datetime import datetime
from io import BytesIO
import json
import logging
from uuid import uuid4

import boto3


logging.basicConfig(level=logging.INFO)


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "aws_access_key_id": config.get("aws", "aws_access_key_id"),
        "aws_secret_access_key": config.get("aws", "aws_secret_access_key"),
        "region": config.get("aws", "region"),
        "sqs_name": config.get("aws", "sqs_name"),
        "sqs_polling_timeout": config.getint("aws", "sqs_polling_timeout"),
        "s3_bucket": config.get("aws", "s3_bucket"),
        "polling_cycles": config.getint("events", "polling_cycles"),
    }


def save_to_dfs(events: list, bucket_name: str, client):
    """
    Saves a list of events to S3 bucket
    :param events: list of raw events
    :param bucket_name: name of S3 bucket
    :param client: boto3 S3 client
    :return: None
    """
    if not events:
        return

    s = BytesIO(bytes(json.dumps(events), 'utf-8'))
    now = datetime.utcnow().strftime("%Y%m%d/%H%M%S")
    filename = f"{now}-{uuid4()}.json"
    client.upload_fileobj(s, bucket_name, filename)
    s.close()
    logging.info("Uploaded %s events to %s", len(events), filename)


def fetch_events(settings: dict):
    """
    Ingest events from SQS and save them to a DFS

    :param settings: settings dictionary
    :return: None
    """
    params = {
        "region_name": settings["region"],
        "aws_access_key_id": settings["aws_access_key_id"],
        "aws_secret_access_key": settings["aws_secret_access_key"]
    }
    s3_client = boto3.client("s3", **params)
    sqs_client = boto3.resource("sqs", **params)

    queue = sqs_client.get_queue_by_name(QueueName=settings["sqs_name"])
    events = []
    cnt = 0

    while True:
        to_delete = []
        for message in queue.receive_messages(MaxNumberOfMessages=10,  # max allowed by boto3
                                              WaitTimeSeconds=settings["sqs_polling_timeout"]):
            try:
                events.append(json.loads(message.body))
            except json.JSONDecodeError:
                logging.error("Could not decode an event ", message.body)
                # The message can potentially be moved to a dead-letter queue for further investigation
                continue

            to_delete.append({"Id": message.message_id, "ReceiptHandle": message.receipt_handle})

        if to_delete:
            queue.delete_messages(Entries=to_delete)

        cnt += 1

        # Save to DFS every `polling_cycles` time
        if cnt >= settings["polling_cycles"]:
            save_to_dfs(events, settings["s3_bucket"], s3_client)
            events = []
            cnt = 0


if __name__ == "__main__":
    settings = load_settings()

    # Start a loop of events fetching
    fetch_events(settings)
